from pyramid.httpexceptions import HTTPBadRequest, HTTPOk
from sqlalchemy.exc import IntegrityError, DataError
import transaction
import json
from src.models import DBSession, So, SoRelation, Dbentity, Alleledbentity, AlleleReference,\
                       Literatureannotation, AlleleAlias, AllelealiasReference, LocusAllele,\
                       LocusalleleReference
from src.curation_helpers import get_curator_session


PARENT_SO_TERM = 'structural variant'

def insert_allele(curator_session, CREATED_BY, source_id, allele_name, so_id):

    a = curator_session.query(Alleledbentity).filter_by(display_name=allele_name).one_or_none()
    if a is not None:
        return a.dbentity_id

    isSuccess = False
    returnValue = ""
    allele_id = None

    x = None
    try:
        format_name = allele_name.replace(" ", "_")
        x = Alleledbentity(format_name = format_name,
                           display_name = allele_name,
                           source_id = source_id,
                           subclass = 'ALLELE',
                           dbentity_status = 'Active',
                           so_id = so_id,
                           created_by = CREATED_BY)
        curator_session.add(x)
        transaction.commit()
        isSuccess = True
        returnValue = "Allele: '" + allele_name + "' added successfully."
    except IntegrityError as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        isSuccess = False
        returnValue = 'Insert allele failed: ' + str(e.orig.pgerror)
    except DataError as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        isSuccess = False
        returnValue = 'Insert allele failed: ' + str(e.orig.pgerror)
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        isSuccess = False
        returnValue = 'Insert allele failed' + ' ' + str(e.orig.pgerror)
    finally:
        allele_id = x.dbentity_id

    if isSuccess:
        return allele_id
    else:
        return returnValue


def get_so_children(parent_id, so_id_list):

    if parent_id not in so_id_list:
        so_id_list.append(parent_id)
        
    so_ids = DBSession.query(SoRelation.child_id).distinct(SoRelation.child_id).filter_by(parent_id=parent_id).all()    
    for so_id in so_ids:
        get_so_children(so_id, so_id_list)

def get_all_allele_types(request):

    try:
        s = DBSession.query(So).filter_by(display_name=PARENT_SO_TERM).one_or_none()
        data = [ { 'so_id': s.so_id,
                   'format_name': s.term_name,
                   'display_name': s.display_name } ]
        so_id_list = []    
        get_so_children(s.so_id, so_id_list)
        for x in DBSession.query(So).filter_by(so_id=so_id).all():
            if x.so_id in so_id_list:
                data.append( { 'so_id': x.so_id,
                               'format_name': x.term_name,
                               'display_name': x.display_name } )        
        return HTTPOk(body=json.dumps(data),content_type='text/json')
    except Exception as e:
        log.error(e)
        return HTTPBadRequest(body=json.dumps({'error': str(e)}))
    finally:
        if DBSession:
            DBSession.remove()
            

def get_one_allele(request):

    try:
        
        data = {}
        allele_name = request.params.get('allele_name')
        a = DBSession.query(Alleledbentity).filter_by(format_name=allele_name).one_or_none()
        data['allele_name'] = a.display_name
        data['format_name'] = a.format_name
        data['sgdid'] = a.sgdid
        data['allele_type'] = a.so.display_name
        data['description'] = a.description
        
        ## get pmids from allele_reference
        allele_name_pmids = []
        description_pmids = []
        allele_type_pmids = []
        other_pmids = []
        for x in DBSession.query(AlleleReference).filter_by(allele_id=a.dbentity_id).all():
            if x.reference_class == 'allele_name':
                allele_name_pmids.append(x.reference.pmid)
            elif x.reference_class == 'description':
                description_pmids.append(x.reference.pmid)
            elif x.reference_class == 'so_term':
                allele_type_pmids.append(x.reference.pmid)
            else:
                other_pmids.append(x.reference.pmid)
        data['allele_name_pmids'] = allele_name_pmids
        data['description_pmids'] = description_pmids
        data['allele_type_pmids'] = allele_type_pmids
        data['other_pmids'] = other_pmids
                
        ## get affected_gene and pmids from locus_allele & locusallele_reference
        x = DBSession.query(LocusAllele).filter_by(allele_id=a.dbentity_id).one_or_none()
        pmids = []
        for y in DBSession.query(LocusalleleReference).filter_by(locus_allele_id=x.locus_allele_id).all():
            pmids.append(y.reference.pmid)

        data['affected_gene'] = { 'display_name': x.locus.display_name,
                                  'sgdid': x.locus.sgdid,
                                  'pmids': pmids } 
            
        ## get aliases and pmids from allele_alias & allelealias_reference
        aliases = []
        for x in DBSession.query(AlleleAlias).filter_by(allele_id=a.dbentity_id).order_by(AlleleAlias.display_name).all():
            pmids = []
            for y in DBSession.query(AllelealiasReference).filter_by(allele_alias_id=x.allele_alias_id).all(): 
                pmids.append(y.reference.pmid)
            aliases.append( { 'display_name': x.display_name,
                              'pmids': pmids } )
        data['aliases'] = aliases
        
        return HTTPOk(body=json.dumps(data),content_type='text/json')
    except Exception as e:
        log.error(e)
        return HTTPBadRequest(body=json.dumps({'error': str(e)}))
    finally:
        if DBSession:
            DBSession.remove()

            
def get_list_of_alleles(request):

    try:
        allele_query = request.params.get('allele_query')
        data = []
        for x in DBSession.query(Alleledbentity).filter(Alleledbentity.display_name.ilike(allele_query)).order_by(Alleledbentity.display_name).all():
            data.append({ 'allele_name': x.display_name,
                          'format_name': x.format_name,
                          'sgdid': x.sgdid,
                          'allele_type': x.so.display_name,
                          'description': x.description })
        return HTTPOk(body=json.dumps(data),content_type='text/json')
    except Exception as e:
        log.ereror(e)
        return HTTPBadRequest(body=json.dumps({'error': str(e)}))
    finally:
        if DBSession:
            DBSession.remove()    


def add_allele_data(request):

    return ""

def update_allele_data(request):

    return ""

def delete_allele_data(request):

    return ""


    
    
