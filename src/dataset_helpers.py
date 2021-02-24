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
                       Filedbentity, Colleague, Keyword
from src.curation_helpers import get_curator_session
from src.metadata_helpers import insert_keyword

log = logging.getLogger('curation')

def insert_dataset_keyword(curator_session, CREATED_BY, source_id, dataset_id, keyword_id):
    
    try:
        x = DatasetKeyword(dataset_id = dataset_id,
                           keyword_id = keyword_id,
                           source_id = source_id,
                           created_by = CREATED_BY)
        curator_session.add(x)
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()

def insert_dataset_file(curator_session, CREATED_BY, source_id, dataset_id, file_id):

    try:
        x = DatasetFile(dataset_id = dataset_id,
                        file_id = file_id,
                        source_id = source_id,
                        created_by = CREATED_BY)
        curator_session.add(x)
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()

def insert_dataset_url(curator_session, CREATED_BY, source_id, dataset_id, display_name, url):

    try:
        x = DatasetUrl(dataset_id = dataset_id,
                       display_name = display_name,
                       obj_url = url,
                       url_type = display_name,
                       source_id = source_id,
                       created_by = CREATED_BY)
        curator_session.add(x)
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()

def insert_datasetlab(curator_session, CREATED_BY, source_id, dataset_id, lab_name, lab_location, colleague_full_name):

    colleague_id = None
    coll = curator_session.query(Colleague).filter_by(full_name = colleague_full_name).one_or_none()
    if coll:
        colleague_id = coll.colleague_id
    
    try:
        x = Datasetlab(dataset_id = dataset_id,
                       lab_name = lab_name,
                       lab_location = lab_location,
                       colleague_id = colleague_id,
                       source_id = source_id,
                       created_by = CREATED_BY)
        curator_session.add(x)
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        
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
        lab = "lab_name: " + labInfo.lab_name + " | lab_location: " + labInfo.lab_location + " | colleague_full_name: "
        if labInfo.colleague_id:
            lab = lab + labInfo.colleague.full_name
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
        # urls = []
        all_dsUrls = DBSession.query(DatasetUrl).filter_by(dataset_id=x.dataset_id).all()
        i = 1
        for dsUrl in all_dsUrls:
            # row = { 'url_type': dsUrl.url_type,
            #        'display_name': dsUrl.display_name,
            #        'link': dsUrl.obj_url }
            # urls.append(row)
            data['url' + str(i)] = dsUrl.display_name + ' | ' + dsUrl.obj_url
            i = i + 1
        # data['urls'] = urls
    
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

        dataset_id = request.params.get('dataset_id', '')
        if dataset_id == '':
            return HTTPBadRequest(body=json.dumps({'error': "No dataset_id is passed in."}), content_type='text/json')
        
        # dataset_format_name = request.params.get('dataset_format_name', '')      
        d = curator_session.query(Dataset).filter_by(dataset_id=int(dataset_id)).one_or_none()
        if d is None:
            return HTTPBadRequest(body=json.dumps({'error': "The dataset_id = " + dataset_id + " is not in the database."}), content_type='text/json')

        dataset_id = d.dataset_id
        
        ## dataset

        update = 0
        format_name = request.params.get('format_name', None)
        if format_name is None:
            return HTTPBadRequest(body=json.dumps({'error': "format_name is required."}), content_type='text/json')
        if format_name != d.format_name:
            d.format_name = format_name
            update = 1
        
        display_name = request.params.get('display_name', '')
        if display_name is None:
            return HTTPBadRequest(body=json.dumps({'error': "display_name is required."}), content_type='text/json')
        if display_name != d.display_name:
            d.display_name = display_name
            update = 1

        dbxref_id = request.params.get('dbxref_id', '')
        if dbxref_id != d.dbxref_id:
            d.dbxref_id = dbxref_id
            update = 1

        dbxref_type = request.params.get('dbxref_type', '')
        if dbxref_type != d.dbxref_type:
            d.dbxref_type = dbxref_type
            update = 1

        date_public = request.params.get('date_public', '')
        if date_public != str(d.date_public).split(' ')[0]:
            d.date_public = date_public
            update = 1
            
        parent_dataset_id = request.params.get('parent_dataset_id', None)
        if str(parent_dataset_id).isdigit():
            parent_dataset_id = int(parent_dataset_id)
            if parent_dataset_id != d.parent_dataset_id:
                d.parent_dataset_id = parent_dataset_id
                update = 1
        elif d.parent_dataset_id:
            d.parent_dataset_id = None
            update = 1

        ## required
        assay_id = request.params.get('assay_id', None)
        if assay_id is None:
            return HTTPBadRequest(body=json.dumps({'error': "assay_id is required."}), content_type='text/json')
        if str(assay_id).isdigit():
            assay_id = int(assay_id)
        if assay_id != d.assay_id:
            d.assay_id = assay_id
            update = 1

        channel_count = request.params.get('channel_count', None)
        if str(channel_count).isdigit():
            channel_count = int(channel_count)
        if channel_count != d.channel_count:
            d.channel_count = channel_count
            update = 1
    
        # required
        sample_count = request.params.get('sample_count', None)
        if sample_count is None:
            return HTTPBadRequest(body=json.dumps({'error': "sample_count is required."}), content_type='text/json')
        if str(sample_count).isdigit():
            sample_count = int(sample_count)
        if sample_count != d.sample_count:
            d.sample_count = sample_count
            update = 1
    
        is_in_spell = request.params.get('is_in_spell')
        is_in_spell = True if is_in_spell == 'true' else False
        if is_in_spell != d.is_in_spell:
            d.is_in_spell = is_in_spell
            update = 1

        is_in_browser = request.params.get('is_in_browser')
        is_in_browser = True if is_in_browser == 'true' else False
        if is_in_browser != d.is_in_browser:
            d.is_in_browser = is_in_browser
            update = 1

        description = request.params.get('description', '')
        if description != d.description:
            d.description = description
            update = 1

        success_message = ''
        if update == 1:
            success_message = 'The dataset table has been successfully updated'

        # return HTTPBadRequest(body=json.dumps({'error': "dataset table"}), content_type='text/json')
    
        ## dataset_file
        
        all_dFile = curator_session.query(DatasetFile).filter_by(dataset_id=dataset_id).all()
        all_file_ids_DB = {}
        for x in all_dFile:
            all_file_ids_DB[x.file_id] = x
            
        filenames = request.params.get('filenames', '')
        files = filenames.split('|')
        
        all_file_ids_NEW = {}
        for file in files:
            if file == '':
                continue
            fd = curator_session.query(Filedbentity).filter_by(display_name=file, subclass='Active').one_or_none()
            if fd is None:
                return HTTPBadRequest(body=json.dumps({'error': "file = " + file + " is not in the database."}), content_type='text/json')
            all_file_ids_NEW[fd.dbentity_id] = fd
            if fd.dbentity_id not in all_file_ids_DB:
                insert_dataset_file(curator_session, CREATED_BY, source_id, dataset_id, fd.dbentity_id)
                success_message = success_message + "<br>file '" + fd.display_name + "' has been added for this dataset."
                
        for file_id in all_file_ids_DB:
            if file_id not in all_file_ids_NEW:
                x = all_file_ids_DB[file_id]
                success_message = success_message + "<br>file '" + fd.display_name + "' has been added for this dataset."
                curator_session.delete(x)

        # return HTTPBadRequest(body=json.dumps({'error': "dataset_file table"}), content_type='text/json')
    
        ## dataset_keyword
        
        all_Kw = curator_session.query(DatasetKeyword).filter_by(dataset_id=dataset_id).all()
        all_keyword_ids_DB = {}
        for x in all_Kw:
            all_keyword_ids_DB[x.keyword_id] = x

        keywords = request.params.get('keywords', '')
        kws = keywords.split('|')

        all_keyword_ids_NEW = {}
        for kw in kws:
            k = curator_session.query(Keyword).filter_by(display_name=kw).one_or_none()
            keyword_id = None
            if k is None:
                keyword_id = insert_keyword(curator_session, CREATED_BY, source_id, kw)
                if str(keyword_id).isdigit():
                    success_message = success_message + "<br>keyword '" + kw + "' has been added into database."
                else:
                    err_msg = keyword_id
                    return HTTPBadRequest(body=json.dumps({'error': err_msg}), content_type='text/json')
            else:
                keyword_id = k.keyword_id
            all_keyword_ids_NEW[keyword_id] = 1
            if keyword_id not in all_keyword_ids_DB:
                insert_dataset_keyword(curator_session, CREATED_BY, source_id, dataset_id, keyword_id)
                success_message = success_message + "<br>keyword '" + kw + "' has been added for this dataset."

        for keyword_id in all_keyword_ids_DB:
            if keyword_id not in all_keyword_ids_NEW:
                x = all_keyword_ids_DB[keyword_id]
                success_message = success_message + "<br>keyword '" + x.display_name + "' has been removed from this dataset."
                curator_session.delete(x)

        # return HTTPBadRequest(body=json.dumps({'error': "dataset_keyword table"}), content_type='text/json')
    
        ## dataset_reference

        all_refs = curator_session.query(DatasetReference).filter_by(dataset_id=dataset_id).all()

        all_ref_ids_DB = {}
        for x in all_refs:
            all_ref_ids_DB[x.reference.dbentity_id] = x

        pmids = request.params.get('pmids', '')
        pmid_list = pmids.split('|')

        all_ref_ids_NEW = {}
        for pmid in pmid_list:
            ref = curator_session.query(Referencedbentity).filter_by(pmid=int(pmid)).one_or_none()
            if ref is None:
                return HTTPBadRequest(body=json.dumps({'error': 'pmid = ' + pmid + ' is not in the database.'}), content_type='text/json')
            reference_id = ref.dbentity_id
            if reference_id not in all_ref_ids_DB:
                insert_dataset_reference(curator_session, CREATED_BY, source_id, dataset_id, reference_id)
                success_message = success_message + "<br>pmid '" + pmid + "' has been added for this dataset."
            all_ref_ids_NEW[reference_id] = 1
                
        for reference_id in all_ref_ids_DB:
            if reference_id not in all_ref_ids_NEW:
                x = all_ref_ids_DB[reference_id]
                success_message = success_message + "<br>pmid '" + pmid + "' has been removed for this dataset."
                curator_session.delete(x)

        # return HTTPBadRequest(body=json.dumps({'error': "dataset_reference table"}), content_type='text/json')
    
        ## dataset_url

        all_urls = curator_session.query(DatasetUrl).filter_by(dataset_id=dataset_id).all()
        
        all_urls_DB = {}
        for x in all_urls:
            all_urls_DB[x.display_name + '|' + x.obj_url] = x

        url1 = request.params.get('url1', '').replace('| ', '|')
        url2 = request.params.get('url2', '').replace(' |', '|')
        url3 = request.params.get('url3', '').replace(' |', '|')
        for url_set in [url1, url2, url3]:
            if url_set == '':
                continue
            if url_set not in all_urls_DB:
                [u_display_name, url] = url_set.split('|')
                u_display_name = u_display_name.strip()
                insert_dataset_url(curator_session, CREATED_BY, source_id, dataset_id, u_display_name, url)
                success_message = success_message + "<br>URL '" + url_set + "' has been added for this dataset."
        for url_set in all_urls_DB:
            if url_set not in [url1, url2, url3]:
                x = all_urls_DB[url_set]
                success_message = success_message + "<br>URL '" + url_set + "' has been removed for this dataset."
                curator_session.delete(x)

        # return HTTPBadRequest(body=json.dumps({'error': "dataset_url table"}), content_type='text/json')
    
        ## datasetlab
        
        labNew = request.params.get('lab', '').replace(' |', '|').replace('| ', '|')
        [lab_name, lab_location, colleague_full_name] =	labNew.split('|')
        lab_name = lab_name.replace('lab_name: ', '')
        lab_location = lab_location.replace('lab_location: ', '')
        colleague_full_name = colleague_full_name.replace('colleague_full_name: ', '')
        
        lab = curator_session.query(Datasetlab).filter_by(dataset_id=dataset_id).one_or_none()
        if lab is not None:
            if lab_name == '' or lab_location == '':
                success_message = success_message + "<br>lab '" + lab.lab_name + '|' + lab.lab_location + "' has been removed for this dataset."
                curator_session.delete(lab)
                
            else: ## update
                update = 0
                if lab.lab_name != lab_name:
                    lab.lab_name = lab_name
                    update = 1
                if lab.lab_location != lab_location:
                    lab.lab_location = lab_location
                    update = 1
                if colleague_full_name:
                    coll = curator_session.query(Colleague).filter_by(full_name=colleague_full_name).one_or_none()
                    colleague_id = None
                    if coll:
                        colleague_id = coll.colleague_id
                    if colleague_id and colleague_id != lab.colleague_id:
                        lab.colleague_id = colleague_id
                        update = 1
                elif lab.colleague_id:
                    lab.colleague_id = None
                    update = 1
                if update == 1:
                    curator_session.add(lab)
                    success_message = success_message + "<br>lab info has been updated for this dataset." 
        elif lab_name and lab_location:
            insert_datasetlab(curator_session, CREATED_BY, source_id, dataset_id, lab_name, lab_location, colleague_full_name)
            success_message = success_message + "<br>lab '" + labNew + "' has been added for this dataset."        

            
        return HTTPBadRequest(body=json.dumps({'error': "dataset_url table"}), content_type='text/json') 
            
            
        if success_message == '':
            success_message = 'Nothing is changed'
        
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

        dataset_id = request.params.get('dataset_id', '')
        if dataset_id == '':
            return HTTPBadRequest(body=json.dumps({'error': "No dataset_id is passed in."}), content_type='text/json')
        d = curator_session.query(Dataset).filter_by(dataset_id=int(dataset_id)).one_or_none()

        if d is None:
            return HTTPBadRequest(body=json.dumps({'error': "The dataset_id = " + dataset_id + " is not in the database."}), content_type='text/json')
        dataset_id = d.dataset_id
        
        ## dataset_file
        all_dFile = curator_session.query(DatasetFile).filter_by(dataset_id=dataset_id).all()
                    
        ## dataset_keyword
        all_dKw = curator_session.query(DatasetKeyword).filter_by(dataset_id=dataset_id).all()
                    
        ## dataset_reference
        all_dRef = curator_session.query(DatasetReference).filter_by(dataset_id=dataset_id).all()
                    
        ## dataset_url
        all_dUrl = curator_session.query(DatasetUrl).filter_by(dataset_id=dataset_id).all()
                    
        ## datasetlab
        all_dLab = curator_session.query(Datasetlab).filter_by(dataset_id=dataset_id).all()
        
        ## datasetsample
        all_dSample = curator_session.query(Datasetsample).filter_by(dataset_id=dataset_id).all()

        ## datasettrack
        all_dTrack = curator_session.query(Datasettrack).filter_by(dataset_id=dataset_id).all()

        for x in all_dFile + all_dKw + all_dRef + all_dUrl + all_dLab + all_dSample + all_dTarck:
            curator_session.delete (x)

        curator_session.delete(d)

        success_message = 'The dataset row along with its associated File/Keyword/URL/Lab/Sample/Track has been successfully deleted.'	

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
            return HTTPBadRequest(body=json.dumps({'error': "The datasetsample_id = " + datasetsample_id + " is not in the database."}), content_type='text/json')

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
        obj_url = request.params.get('obj_url', '')
        track_order = request.params.get('track_order', '')

        if format_name == '' or display_name == '' or obj_url == '' or track_order == '':
            return HTTPBadRequest(body=json.dumps({'error': "All four fields are required."}), content_type='text/json')
        
        update = 0
        if format_name != d.format_name:
            d.format_name = format_name
            update = 1
        if display_name != d.display_name:
            d.display_name = display_name
            update = 1
        if obj_url != d.obj_url:
            d.obj_url = obj_url
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
