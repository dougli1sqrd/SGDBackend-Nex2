from sqlalchemy import or_
from pyramid.httpexceptions import HTTPBadRequest, HTTPOk
from sqlalchemy.exc import IntegrityError, DataError
import transaction
import json
from src.models import DBSession, So, SoRelation, Dbentity, Alleledbentity, AlleleReference,\
                       Literatureannotation, AlleleAlias, AllelealiasReference, LocusAllele,\
                       LocusalleleReference, Referencedbentity, Locusdbentity, Taxonomy, Source
from src.curation_helpers import get_curator_session


PARENT_SO_TERM = 'structural variant'
TAXON = 'TAX:4932'

def insert_locusallele_reference(curator_session, CREATED_BY, source_id, locus_allele_id, reference_id):

    x = None
    try:
        x = LocusalleleReference(locus_allele_id = locus_allele_id,
                                 reference_id = reference_id,
                                 source_id = source_id,
                                 created_by = CREATED_BY)
        curator_session.add(x)
        # transaction.commit()
        return 1
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        return str(e)

def insert_allelealias_reference(curator_session, CREATED_BY, source_id, allele_alias_id, reference_id):

    x = None
    try:
        x = AllelealiasReference(allele_alias_id = allele_alias_id,
                                 reference_id = reference_id,
                                 source_id = source_id,
                                 created_by = CREATED_BY)
        curator_session.add(x)
        # transaction.commit()
        return 1
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        return str(e)

def insert_allele_reference(curator_session, CREATED_BY, source_id, allele_id, reference_id, reference_class):

    x = None
    try:
        x = AlleleReference(allele_id = allele_id,
                            reference_id = reference_id,
                            reference_class = reference_class,
                            source_id = source_id,
                            created_by = CREATED_BY)
        curator_session.add(x)
        # transaction.commit()
        return 1
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        return str(e)

    
def insert_literatureannotation(curator_session, CREATED_BY, source_id, allele_id, reference_id, topic, taxonomy_id):

    x = None
    try:
        x = Literatureannotation(dbentity_id = allele_id,
                                 reference_id = reference_id,
                                 topic = topic,
                                 taxonomy_id = taxonomy_id,
                                 source_id = source_id,
                                 created_by = CREATED_BY)
        curator_session.add(x)
        # transaction.commit()
        return 1
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        return str(e)
    
def insert_allele_alias(curator_session, CREATED_BY, source_id, allele_id, alias_name):

    x = None
    try:
        x = AlleleAlias(allele_id = allele_id,
                        display_name = alias_name,
                        source_id = source_id,
                        alias_type = 'Synonym',
                        created_by = CREATED_BY)
        curator_session.add(x)
        # transaction.commit()
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        return str(e)
    finally:
        curator_session.flush()
        curator_session.refresh(x)
        return x.allele_alias_id

    
def insert_locus_allele(curator_session, CREATED_BY, source_id, allele_id, locus_id):

    x = None
    try:
        x = LocusAllele(allele_id = allele_id,
                        locus_id = locus_id,
                        source_id = source_id,
                        created_by = CREATED_BY)
        curator_session.add(x)
        # transaction.commit()    
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        return str(e)
    finally:
        curator_session.flush()
        curator_session.refresh(x)
        return x.locus_allele_id

def insert_allele(curator_session, CREATED_BY, source_id, allele_name, so_id, desc):

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
                           description = desc,
                           created_by = CREATED_BY)
        curator_session.add(x)
        # transaction.commit()
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
        curator_session.flush()
        curator_session.refresh(x)
        allele_id = x.dbentity_id

    if isSuccess:
        return allele_id
    else:
        return returnValue

        
def get_all_allele_types(request):

    try:        
        parent_id_to_child_ids = {}
        for x in DBSession.query(SoRelation).all():
            child_ids = []
            if x.parent_id in parent_id_to_child_ids:
                child_ids = parent_id_to_child_ids[x.parent_id]
            child_ids.append(x.child_id)
            parent_id_to_child_ids[x.parent_id] = child_ids
        
        s = DBSession.query(So).filter_by(display_name=PARENT_SO_TERM).one_or_none()
        so_id_list = [s.so_id]
        for so_id in so_id_list:
            child_ids = parent_id_to_child_ids.get(so_id, [])
            for child_id in child_ids:
                if child_id is not so_id_list:
                    so_id_list.append(child_id)
        
        data = []
        so_id_to_so = dict([(x.so_id, x) for x in DBSession.query(So).all()])
        for so_id in so_id_list:
            so = so_id_to_so[so_id]
            data.append( { 'so_id': so_id,
                           'format_name': so.term_name,
                           'display_name': so.display_name } )
            
        return HTTPOk(body=json.dumps(data), content_type='text/json')
        
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}))
    finally:
        if DBSession:
            DBSession.remove()

        
def get_one_allele(request):

    try:
        
        data = {}
        
        allele_format_name = str(request.matchdict['allele_format_name'])
    
        a = DBSession.query(Alleledbentity).filter_by(format_name=allele_format_name).one_or_none()
        
        if a is None:
            return HTTPBadRequest(body=json.dumps({'error': "The allele format_name " + allele_format_name + " is not in the database."}))
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
                alleles_type_pmids.append(x.reference.pmid)
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


def check_pmids(pmids, pmid_to_reference_id):

    reference_ids = []
    bad_pmids = []
    for pmid in pmids.split(' '):
        if pmid == '':
            continue
        if int(pmid) not in pmid_to_reference_id:
            if pmid not in bad_pmids:
                bad_pmids.append(pmid)
            continue
        reference_id = pmid_to_reference_id[int(pmid)]
        if (reference_id, pmid) not in reference_ids:
            reference_ids.append((pmid_to_reference_id[int(pmid)], pmid))
    err_message = ''
    if len(bad_pmids) > 0:
        err_message = "The PMID(s):" + ', '.join(bad_pmids) + " are not in the database"
    return (reference_ids, err_message)
    

def get_pmid_to_reference_id():

    pmid_to_reference_id = dict([(x.pmid, x.dbentity_id) for x in DBSession.query(Referencedbentity).all()])

    return pmid_to_reference_id


def add_allele_data(request):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])
        sgd = DBSession.query(Source).filter_by(display_name='SGD').one_or_none()
        source_id = sgd.source_id

        ## allele name & references
        
        allele_name = request.params.get('allele_name')
        if allele_name == '':
            return HTTPBadRequest(body=json.dumps({'error': "Allele name field is blank"}), content_type='text/json')
        so_id = request.params.get('so_id')
        if so_id and str(so_id).isdigit():
            so_id = int(so_id)
        else:
            return HTTPBadRequest(body=json.dumps({'error': "Allele type field is blank"}), content_type='text/json')

        desc = request.params.get('desc')

        # return HTTPBadRequest(body=json.dumps({'error': "ALLELE_NAME"}), content_type='text/json')
        
        returnValue = insert_allele(curator_session, CREATED_BY, source_id, allele_name, so_id, desc)
        allele_id = None
        success_message = ""
        if str(returnValue).isdigit():
            allele_id = returnValue
            success_message = success_message + "<br>" + "The new allele '" + allele_name + "' has been added into DBENTITY/ALLELEDBENTITY tables. "
        else:
            return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')

        
        # return HTTPBadRequest(body=json.dumps({'error': "allele_id="+str(allele_id)}), content_type='text/json')
    
        
        allele_name_pmids = request.params.get('allele_name_pmids')

        
        # return HTTPBadRequest(body=json.dumps({'error': "allele_name_pmids="+str(allele_name_pmids)}), content_type='text/json')

        pmid_to_reference_id = get_pmid_to_reference_id()

        (reference_ids, err_message) = check_pmids(allele_name_pmids, pmid_to_reference_id)
    
        if err_message != '':
            return HTTPBadRequest(body=json.dumps({'error': err_message}), content_type='text/json')

        for (reference_id, pmid) in reference_ids:
            returnValue = insert_allele_reference(curator_session, CREATED_BY, source_id,
                                                  allele_id, reference_id, "allele_name")
            if returnValue != 1:
                return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')
            success_message = success_message + "<br>" + "The paper for PMID= " + pmid + " has been added into ALLELE_REFERENCE table for 'allele_name'. "

        # return HTTPBadRequest(body=json.dumps({'error': "allele_name reference_ids="+str(reference_ids)}), content_type='text/json')

      
        ## affected gene & reference(s)
        
        affected_gene = request.params.get('affected_gene')

        if allele_name.upper().startswith(affected_gene.upper()):
            locus = DBSession.query(Locusdbentity).filter(or_(Locusdbentity.gene_name.ilike(affected_gene), Locusdbentity.systematic_name.ilike(affected_gene))).one_or_none()
            if locus is None:
                return HTTPBadRequest(body=json.dumps({'error': "The affected gene name " + affected_gene + " is not in the database."}), content_type='text/json')
            locus_id = locus.dbentity_id
            returnValue = insert_locus_allele(curator_session, CREATED_BY, source_id, allele_id, locus_id)
            locus_allele_id = None
            if str(returnValue).isdigit():
                locus_allele_id = returnValue
                success_message = success_message + "<br>" + "The affected gene '" + affected_gene + "' has been added into LOCUS_ALLELE table. "
            else:
                return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')


            # return HTTPBadRequest(body=json.dumps({'error': "locus_id="+str(locus_id)}), content_type='text/json')

            
            affected_gene_pmids = request.params.get('affected_gene_pmids')

            # return HTTPBadRequest(body=json.dumps({'error': "affected_gene_pmids="+affected_gene_pmids}), content_type='text/json')
                
            (reference_ids, err_message) = check_pmids(affected_gene_pmids, pmid_to_reference_id)

            
            # return HTTPBadRequest(body=json.dumps({'error': "reference_ids="+str(reference_ids)}), content_type='text/json')

            
            if err_message != '':
                return HTTPBadRequest(body=json.dumps({'error': err_message}), content_type='text/json')
            
            for (reference_id, pmid) in reference_ids:
                returnValue = insert_locusallele_reference(curator_session, CREATED_BY, source_id,
                                                           locus_allele_id, reference_id)
                if returnValue != 1:
                    return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')
                success_message = success_message + "<br>" + "The paper for PMID= " + pmid + " has been added into LOCUSALLELE_REFERENCE table. "
                
            # return HTTPBadRequest(body=json.dumps({'error': "reference_ids="+str(reference_ids)}), content_type='text/json')
  
        else:
            return HTTPBadRequest(body=json.dumps({'error': "The affected gene name " + affected_gene + " doesn't match allele_name " + allele_name + "."}), content_type='text/json')

        
        ## allele type & reference(s)
        
        allele_type_pmids = request.params.get('allele_type_pmids')
        (reference_ids, err_message) = check_pmids(allele_type_pmids, pmid_to_reference_id)

        # return HTTPBadRequest(body=json.dumps({'error': "allele_type reference_ids="+str(reference_ids)}), content_type='text/json')   
    
        if err_message != '':
            return HTTPBadRequest(body=json.dumps({'error': err_message}), content_type='text/json')

        for (reference_id, pmid) in reference_ids:
            returnValue = insert_allele_reference(curator_session, CREATED_BY, source_id,
                                                  allele_id, reference_id, "so_term")
            if returnValue != 1:
                return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')
            success_message = success_message + "<br>" + "The paper for PMID= " + pmid + " has been added into ALLELE_REFERENCE table for 'so_term'. "
            
        ## references for description
        
        desc_pmids = request.params.get('desc_pmids')

        (reference_ids, err_message) = check_pmids(desc_pmids, pmid_to_reference_id)

        # return HTTPBadRequest(body=json.dumps({'error': "description reference_ids="+str(reference_ids)}), content_type='text/json')
                
        if err_message != '':
            return HTTPBadRequest(body=json.dumps({'error': err_message}), content_type='text/json')

        for (reference_id, pmid) in reference_ids:
            returnValue = insert_allele_reference(curator_session, CREATED_BY, source_id,
                                                  allele_id, reference_id, "allele_description")
            if returnValue != 1:
                return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')
            success_message = success_message + "<br>" + "The paper for PMID= " + pmid + " has been added into ALLELE_REFERENCE table for 'allele_description'. "

        ## aliases & reference(s)
        
        alias_list = request.params.get('aliases', '')
        alias_pmid_list = request.params.get('alias_pmids', '')

        aliases = alias_list.strip().split('|')
        alias_pmids = alias_pmid_list.strip().split('|')
                    
        if len(aliases) != len(alias_pmids):
            return HTTPBadRequest(body=json.dumps({'error': "Provide same number of PMID sets for alias(es)"}), content_type='text/json')
        
        i = 0
        for alias_name in aliases:
            alias_name = alias_name.strip()
            if alias_name == '':
                i = i + 1
                continue       
            (reference_ids, err_message) = check_pmids(alias_pmids[i], pmid_to_reference_id)
            if err_message != '':
                return HTTPBadRequest(body=json.dumps({'error': err_message}), content_type='text/json')
            returnValue = insert_allele_alias(curator_session, CREATED_BY, source_id,
                                              allele_id, alias_name)
            i = i + 1
            allele_alias_id = None
            if str(returnValue).isdigit():
                allele_alias_id = returnValue
                success_message = success_message + "<br>" + "The new alias " + alias_name + " has been added into ALLELE_ALIAS table. "
            else:
                return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')


            
            # return HTTPBadRequest(body=json.dumps({'error': "allele_alias_id="+str(allele_alias_id) + ", reference_ids="+str(reference_ids)}), content_type='text/json')

        
    
            for (reference_id, pmid) in reference_ids:
                returnValue = insert_allelealias_reference(curator_session, CREATED_BY, source_id,
                                                           allele_alias_id, reference_id)
                if returnValue != 1:
                    return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')
                success_message = success_message + "<br>" + "The paper for PMID= " + pmid + " has been added into ALLELEALIAS_REFERENCE table for alias " + alias_name + ". "


                
        ## papers for primary literacture

        taxonomy = DBSession.query(Taxonomy).filter_by(taxid=TAXON).one_or_none()
        taxonomy_id = taxonomy.taxonomy_id

    
        # return HTTPBadRequest(body=json.dumps({'error': "PRIMARY LITERATURE"}), content_type='text/json')

    
        primary_pmids = request.params.get('primary_pmids')

        (reference_ids, err_message) = check_pmids(primary_pmids, pmid_to_reference_id)
        if err_message != '':
            return HTTPBadRequest(body=json.dumps({'error': err_message}), content_type='text/json')

        for (reference_id, pmid) in reference_ids:
            returnValue = insert_literatureannotation(curator_session, CREATED_BY, source_id, allele_id,
                                                      reference_id, 'Primary Literature', taxonomy_id) 
            if returnValue != 1:
                return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')
            success_message = success_message + "<br>" + "The primary literature for PMID= " + pmid + " has been added into LITERATUREANNOTATION table. "
            
        ## papers for additional literacture
        
        additional_pmids = request.params.get('additional_pmids')

        (reference_ids, err_message) = check_pmids(additional_pmids, pmid_to_reference_id)
        if err_message != '':
            return HTTPBadRequest(body=json.dumps({'error': err_message}), content_type='text/json')

        for (reference_id, pmid) in reference_ids:
            returnValue = insert_literatureannotation(curator_session, CREATED_BY, source_id, allele_id,
                                                      reference_id, 'Additional Literature', taxonomy_id)
            if returnValue != 1:
                return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')
            success_message = success_message + "<br>" + "The additional literature for PMID= " + pmid + " has been added into LITERATUREANNOTATION table. "

        ## papers for review literacture
        
        review_pmids = request.params.get('review_pmids')
        
        (reference_ids, err_message) = check_pmids(review_pmids, pmid_to_reference_id)
        if err_message != '':
            return HTTPBadRequest(body=json.dumps({'error': err_message}), content_type='text/json')

        for (reference_id, pmid) in reference_ids:
            returnValue = insert_literatureannotation(curator_session, CREATED_BY, source_id, allele_id,
                                                      reference_id, 'Reviews', taxonomy_id)
            if returnValue != 1:
                return HTTPBadRequest(body=json.dumps({'error': returnValue}), content_type='text/json')
            success_message = success_message + "<br>" + "The reviews literature for PMID= " + pmid + " has been added into LITERATUREANNOTATION table. "
        
        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'allele': "ALLELE"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()

def update_allele_data(request):

    return ""

def delete_allele_data(request):

    return ""


    
    
