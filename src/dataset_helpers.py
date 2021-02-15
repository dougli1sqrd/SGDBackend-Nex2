import logging
import os
import datetime
from sqlalchemy import or_
from pyramid.httpexceptions import HTTPBadRequest, HTTPOk
from sqlalchemy.exc import IntegrityError, DataError
import transaction
import json
from src.models import DBSession, Dataset, Datasetsample, Datasettrack, Datasetlab, DatasetFile, \
                       DatasetKeyword, DatasetReference, DatasetUrl, Referencedbentity, Source
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

    return []

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
