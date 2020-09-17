from pyramid.httpexceptions import HTTPBadRequest, HTTPOk
from sqlalchemy.exc import IntegrityError, DataError
import transaction
import json
from src.models import DBSession, So, SoRelation, Dbentity, Alleledbentity, AlleleReference,\
                       Literatureannotation, AlleleAlias, AllelealiasReference, LocusAllele,\
                       LocusalleleReference
from src.curation_helpers import get_curator_session


PARENT_SO_TERM = 'structural variant'

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
            


    
    
