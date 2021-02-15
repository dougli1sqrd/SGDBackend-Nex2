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
                          'date_public': str(x.date_public) })
        return HTTPOk(body=json.dumps(data),content_type='text/json')
    except Exception as e:
        log.error(e)
        return HTTPBadRequest(body=json.dumps({'error': str(e)}))
    finally:
        if DBSession:
            DBSession.remove()
            
def get_one_dataset(request):

    try:
        data = {}
        format_name = str(request.matchdict['format_name'])
        x = DBSession.query(Dataset).filter_by(format_name=format_name).one_or_none()
        if x is None:
            return HTTPBadRequest(body=json.dumps({'error': "The dataset format_name " + format_name + " is not in the database."}))
        data['format_name'] = x.format_name
        data['display_name'] = x.display_name
        data['dbxref_id'] = x.dbxref_id
        data['dbxref_type'] = x.dbxref_type
        data['date_public'] = str(x.date_public).split(' ')[0]
        data['parent_dataset_id'] = x.parent_dataset_id
        data['assay_id'] = x.assay_id
        data['channel_count'] = x.channel_count
        data['sample_count'] = x.sample_count
        data['is_in_spell'] = x.is_in_spell
        data['is_in_browser'] = x.is_in_browser
        data['description'] = x.description
    
        ## file names
        files = ''
        all_dfs = DBSession.query(DatasetFile).filter_by(dataset_id=x.dataset_id).all() 
        for df in all_dfs:
            if df.file.dbentity_status == 'Active':
                if files != '':
                    files = files + '|'
                files = files + df.file.display_name 
        data['filenames'] = files

        ## keywords
        keywords = ''
        all_kws = DBSession.query(DatasetKeyword).filter_by(dataset_id=x.dataset_id).all()
        for kw in all_kws:
            if keywords != '':
                keywords = keywords + '|'
            keywords = keywords + kw.keyword.display_name
        data['keywords'] = keywords
    
        ## pmids
        pmids = ''
        all_dsRefs = DBSession.query(DatasetReference).filter_by(dataset_id=x.dataset_id).all()
        for dsR in all_dsRefs:
            if pmids != '':
                pmids = pmids + '|'
            pmids = pmids + str(dsR.reference.pmid)
        data['pmids'] = pmids

        return data
    
        ## urls
        urls = []
        all_dsUrls = DBSession.query(DatasetUrl).filter_by(dataset_id=x.dataset_id).all()
        for dsUrl in all_dsUrls:
            row = { 'url_type': dsUrl.url_type,
                    'display_name': dsUrl.display_name,
                    'link': dsUrl.obj_url }
            urls.append(row)
        data['urls'] = urls

        ## lab
        labInfo = DBSession.query(Datasetlab).filter_by(dataset_id=x.dataset_id).one_or_none()
        lab = ''
        if labInfo is not None:
            lab = labInfo.lab_name + ", " + labInfo.lab_location
            if labInfo.colleague_id:
                lab = labInfo.colleague.full_name + " @" + lab 
        data['lab'] = lab

        ## samples
        samples = []
        all_samples = DBSession.query(Datasetsample).filter_by(dataset_id=x.dataset_id).all()
        for s in all_samples:
            samples.append({ 'format_name': s.format_name,
                             'display_name': s.display_name,
                             'obj_url': s.obj_url,
                             'taxonomy_id': s.taxonomy_id,
                             'sample_order': s.sample_order,
                             'dbxref_id': s.dbxref_id,
                             'dbxref_type': s.dbxref_type,
                             'biosample': s.biosample,
                             'strain_name': s.strain_name,
                             'description': s.description,
                             'dbxref_url': s.dbxref_url })
        data['samples'] = samples
        
        ## tracks
        tracks = []
        all_tracks = DBSession.query(Datasettrack).filter_by(dataset_id=x.dataset_id).all()
        for t in all_tracks:
            tracks.append({ 'format_name': t.format_name,
                            'display_name': t.display_name,
                            'obj_url': t.obj_url,
                            'track_order': t.track_order })
        data['tracks'] = tracks

        return HTTPOk(body=json.dumps(data),content_type='text/json')
    except Exception as e:
        log.error(e)
        return HTTPBadRequest(body=json.dumps({'error': str(e)}))
    finally:
        if DBSession:
            DBSession.remove()
            
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
