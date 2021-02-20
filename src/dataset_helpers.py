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

def get_pmids(dataset_id):
    
    pmids = ''
    all_dsRefs = DBSession.query(DatasetReference).filter_by(dataset_id=dataset_id).all()
    for dsR in all_dsRefs:
        if pmids != '':
            pmids = pmids + '|'
        pmids = pmids + str(dsR.reference.pmid)
    return pmids

def get_keywords(dataset_id):
    
    keywords = ''
    all_kws = DBSession.query(DatasetKeyword).filter_by(dataset_id=dataset_id).all()
    for kw in all_kws:
        if keywords != '':
            keywords = keywords + '|'
        keywords = keywords + kw.keyword.display_name
    return keywords

def get_lab(dataset_id):
                                                                                            
    labInfo = DBSession.query(Datasetlab).filter_by(dataset_id=dataset_id).one_or_none()
    lab = ''
    if labInfo is not None:
        lab = labInfo.lab_name + ", " + labInfo.lab_location
        if labInfo.colleague_id:
            lab = labInfo.colleague.full_name + " @" + lab
    return lab

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
            pmids = get_pmids(x.dataset_id)
            keywords = get_keywords(x.dataset_id)
            lab = get_lab(x.dataset_id)
            data.append({ 'format_name': x.format_name,
                          'display_name': x.display_name,
                          'dbxref_id': x.dbxref_id,
                          'dbxref_type': x.dbxref_type,
                          'date_public': str(x.date_public),
                          'pmids': pmids,
                          'keywords': keywords,
                          'lab': lab })
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
        data['dataset_id'] = x.dataset_id
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

        ## pmids, keywords, lab
        data['pmids'] = get_pmids(x.dataset_id)
        data['keywords'] = get_keywords(x.dataset_id)
        data['lab'] = get_lab(x.dataset_id)
        
        ## urls
        urls = []
        all_dsUrls = DBSession.query(DatasetUrl).filter_by(dataset_id=x.dataset_id).all()
        for dsUrl in all_dsUrls:
            row = { 'url_type': dsUrl.url_type,
                    'display_name': dsUrl.display_name,
                    'link': dsUrl.obj_url }
            urls.append(row)
        data['urls'] = urls
    
        ## samples
        samples = []
        all_samples = DBSession.query(Datasetsample).filter_by(dataset_id=x.dataset_id).order_by(Datasetsample.sample_order).all()
        for s in all_samples:
            samples.append({ 'datasetsample_id': s.datasetsample_id,
                             'format_name': s.format_name,
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
        all_tracks = DBSession.query(Datasettrack).filter_by(dataset_id=x.dataset_id).order_by(Datasettrack.track_order).all()
        for t in all_tracks:
            tracks.append({ 'datasettrack_id': t.datasettrack_id,
                            'format_name': t.format_name,
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

        datasetsample_id = request.params.get('datasetsample_id', '')
        if datasetsample_id == '':
            return HTTPBadRequest(body=json.dumps({'error': "No datasetsample_id is passed in."}), content_type='text/json')
        d = curator_session.query(Datasetsample).filter_by(datasetsample_id=int(datasetsample_id)).one_or_none()

        if d is None:
            return HTTPBadRequest(body=json.dumps({'error': "The datasetsample_id " + datasetsample_id + " is not in the database."}), content_type='text/json')

        format_name = request.params.get('format_name', '')
        display_name = request.params.get('display_name', '')
        dbxref_id = request.params.get('dbxref_id', '')
        dbxref_type = request.params.get('dbxref_type', '')
        dbxref_url = request.params.get('dbxref_url', '')
        strain_name = request.params.get('strain_name', '')
        biosample = request.params.get('biosample', '')
        sample_order = request.params.get('sample_order', '') 
        description = request.params.get('description', '')

        if format_name == '' or display_name == '' or sample_order == '':
            return HTTPBadRequest(body=json.dumps({'error': "format_name, display_name, and sample_order are required fields."}), content_type='text/json')
        update = 0
        if format_name != d.format_name:
            d.format_name = format_name
            update = 1
        if display_name != d.display_name:
            d.display_name = display_name
            update = 1
        if dbxref_id != d.dbxref_id:
            d.dbxref_id = dbxref_id
            update = 1
        if dbxref_type != d.dbxref_type:
            d.dbxref_type = dbxref_type
            update = 1
        if dbxref_url != d.dbxref_url:
            d.dbxref_url = dbxref_url
            update = 1
        if strain_name != d.strain_name:
            d.strain_name = strain_name
            update = 1
        if biosample != d.biosample:
            d.biosample = biosample
            update = 1
        if int(sample_order) != d.sample_order:
            d.sample_order = int(sample_order)
            update = 1
        if description != d.description:
            d.description = description
            update = 1
            
        success_message = ''
        if update == 1:
            curator_session.add(d)
            success_message = 'The datasetsample row has been successfully updated'
        else:
            success_message = 'Nothing is changed'
            
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

        datasetsample_id = request.params.get('datasetsample_id', '')
        if datasetsample_id == '':
            return HTTPBadRequest(body=json.dumps({'error': "No datasetsample_id is passed in."}), content_type='text/json')
        d = curator_session.query(Datasetsample).filter_by(datasetsample_id=int(datasetsample_id)).one_or_none()

        if d is None:
            return HTTPBadRequest(body=json.dumps({'error': "The datasetsample_id " + datasettrack_id + " is not in the database."}), content_type='text/json')

        curator_session.delete(d)

        success_message = 'The datasetsample row has been successfully deleted.'
        
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

        datasettrack_id = request.params.get('datasettrack_id', '')
        if datasettrack_id == '':
            return HTTPBadRequest(body=json.dumps({'error': "No datasettrack_id is passed in."}), content_type='text/json')
        d = curator_session.query(Datasettrack).filter_by(datasettrack_id=int(datasettrack_id)).one_or_none()

        if d is None:
            return HTTPBadRequest(body=json.dumps({'error': "The datasettrack_id " + datasettrack_id + " is not in the database."}), content_type='text/json')
        
        format_name = request.params.get('format_name', '')
        display_name = request.params.get('display_name', '')
        dbxref_id = request.params.get('dbxref_id', '')
        track_order = request.params.get('track_order', '')

        if format_name == '' or diplay_name == '' or dbxref_id == '' or track_order == '':
            return HTTPBadRequest(body=json.dumps({'error': "All four fields are required."}), content_type='text/json')
        
        update = 0
        if format_name != d.format_name:
            d.format_name = format_name
            update = 1
        if display_name != d.display_name:
            d.display_name = display_name
            update = 1
        if dbxref_id != d.dbxref_id:
            d.dbxref_id = dbxref_id
            update = 1
        if track_order != d.track_order:
            d.track_order = track_order
            update = 1
            
        success_message = ''
        if update == 1:
            curator_session.add(d)
            success_message = 'The datasettrack row has been successfully updated.'
        else:
            success_message = 'Nothing is changed'
            
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
        
        datasettrack_id = request.params.get('datasettrack_id', '')
        if datasettrack_id == '':
            return HTTPBadRequest(body=json.dumps({'error': "No datasettrack_id is passed in."}), content_type='text/json')
        d = curator_session.query(Datasettrack).filter_by(datasettrack_id=int(datasettrack_id)).one_or_none()

        if d is None:
            return HTTPBadRequest(body=json.dumps({'error': "The datasettrack_id " + datasettrack_id + " is not in the database."}), content_type='text/json')

        curator_session.delete(d)

        success_message = 'The datasettrack row has been successfully deleted.'
        
        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'dataset': "DATASET"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()
