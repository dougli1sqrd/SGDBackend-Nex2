import logging
import os
import datetime
from sqlalchemy import or_
from pyramid.httpexceptions import HTTPBadRequest, HTTPOk
from sqlalchemy.exc import IntegrityError, DataError
import transaction
import json
from src.models import DBSession, Dataset, Datasetsample, Datasettrack, Datasetlab, DatasetFile, \
                       DatasetKeyword, DatasetReference, DatasetUrl, Referencedbentity, Source,\
                       Filedbentity
from src.curation_helpers import get_curator_session

# PREVIEW_URL = os.environ['PREVIEW_URL']

log = logging.getLogger('curation')

def insert_dataset_reference(curator_session, CREATED_BY, source_id, dataset_id, reference_id):

    try:
        x = DatasetReference(dataset_id = dataset_id,
                             reference_id = reference_id,
                             source_id = source_id,
                             created_by = CREATED_BY)
        curator_session.add(x)
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()

def get_list_of_dataset(request):

    try:
        query = str(request.matchdict['query'])
        data = []

        ## search by PMID:
        rows_by_pmid = []
        if query.isdigit():
            pmid = int(query)
            ref = DBSession.query(Referencedbentity).filter_by(pmid=pmid).one_or_none()
            if ref is not None:
                all_dsRefs = DBSession.query(DatasetReference).filter_by(reference_id=ref.dbentity_id).all()
                for x in all_dsRefs:
                    rows_by_pmid.append(x.dataset)

        ## search by GEO/SRA/ArrayExpress ID:
        rows_by_GEO = DBSession.query(Dataset).filter(Dataset.format_name.ilike('%'+query+'%')).all()

        ## search by file name:
        rows_by_filename = []
        all_fileRows = DBSession.query(Filedbentity).filter(or_(Filedbentity.display_name.ilike('%'+query+'%'), Filedbentity.previous_file_name.ilike('%'+query+'%'))).order_by(Filedbentity.display_name).all()
        for x in all_fileRows:
            all_dsFiles = DBSession.query(DatasetFile).filter_by(file_id=x.dbentity_id).all()
            for y in all_dsFiles:
                rows_by_filename.append(y.dataset)
        
        foundDataset = {}    
        for x in rows_by_pmid + rows_by_GEO + rows_by_filename:
            if x.format_name in foundDataset:
                continue
            foundDataset[x.format_name] = 1
            data.append({ 'format_name': x.format_name,
                          'display_name': x.display_name,
                          'dbxref_id': x.dbxref_id,
                          'dbxref_type': x.dbxref_type,
                          'date_public': x.date_public })
        return HTTPOk(body=json.dumps(data),content_type='text/json')
    except Exception as e:
        log.error(e)
        return HTTPBadRequest(body=json.dumps({'error': str(e)}))
    finally:
        if DBSession:
            DBSession.remove()
            
def get_one_dataset(request):

    return {}

def load_dataset(request):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])
        sgd = DBSession.query(Source).filter_by(display_name='SGD').one_or_none()
        source_id = sgd.source_id

        success_message = ''
	

        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'dataset': "DATASET"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()

            
def update_dataset(request):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])
        sgd = DBSession.query(Source).filter_by(display_name='SGD').one_or_none()
        source_id = sgd.source_id

        success_message = ''
        

        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'dataset': "DATASET"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()

def delete_dataset(request):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])


        success_message = ''
	

        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'dataset': "DATASET"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()

def update_datasetsample(request):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])
        sgd = DBSession.query(Source).filter_by(display_name='SGD').one_or_none()
        source_id = sgd.source_id

        success_message = ''
	

        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'dataset': "DATASET"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()

def delete_datasetsample(request):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])
        

        success_message = ''
	

        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'dataset': "DATASET"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()
            
def update_datasettrack(request):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])
        sgd = DBSession.query(Source).filter_by(display_name='SGD').one_or_none()
        source_id = sgd.source_id

        success_message = ''
	

        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'dataset': "DATASET"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()

def delete_datasettrack(request):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])
        
        success_message = ''
	

        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'dataset': "DATASET"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()
