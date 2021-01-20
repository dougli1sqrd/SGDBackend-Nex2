import logging
import os
from sqlalchemy import or_
from pyramid.httpexceptions import HTTPBadRequest, HTTPOk
from sqlalchemy.exc import IntegrityError, DataError
import transaction
import json
from src.models import DBSession, Dbentity, Filedbentity, FilePath, Path,\
                       FileKeyword, Keyword
from src.curation_helpers import get_curator_session

# PREVIEW_URL = os.environ['PREVIEW_URL']

log = logging.getLogger('curation')

def get_metadata_for_one_file(request):

    try:
        
        data = {}
        
        sgdid = str(request.matchdict['sgdid'])
    
        x = DBSession.query(Filedbentity).filter_by(sgdid=sgdid).one_or_none()
        
        if x is None:
            return HTTPBadRequest(body=json.dumps({'error': "The file sgdid " + sgdid + " is not in the database."}))
        
        data['display_name'] = x.display_name
        data['previous_file_name'] = x.previous_file_name
        data['sgdid'] = x.sgdid
        data['dbentity_status'] = x.dbentity_status
        data['file_extension'] = x.file_extension
        data['file_date'] = str(x.file_date).split(' ')[0]
        data['is_public'] = x.is_public
        data['is_in_spell'] = x.is_in_spell
        data['is_in_browser'] = x.is_in_browser
        data['md5sum'] = x.md5sum
        data['readme_file_id'] = x.readme_file_id
        data['s3_url'] = x.s3_url
        data['description'] = x.description
        data['year'] = x.year
        data['file_size'] = x.file_size
        data['topic_id'] = x.topic_id
        data['data_id'] = x.data_id
        data['format_id'] = x.format_id

        all_kw = DBSession.query(FileKeyword).filter_by(file_id=x.dbentity_id).all()
        keywords = []
        for kw in all_kw:
            keywords.append(kw.keyword.display_name)
        data['keywords'] = '|'.join(keywords)

        fp = DBSession.query(FilePath).filter_by(file_id=x.dbentity_id).one_or_none()
        if fp is not None:
            data['path_id'] = fp.path_id
        else:
            data['path_id'] = ''
            
        return HTTPOk(body=json.dumps(data),content_type='text/json')
    except Exception as e:
        log.error(e)
        return HTTPBadRequest(body=json.dumps({'error': str(e)}))
    finally:
        if DBSession:
            DBSession.remove()

            
def get_list_of_file_metadata(request):

    try:
        query = str(request.matchdict['query'])
        data = []
        for x in DBSession.query(Filedbentity).filter(or_(Filedbentity.display_name.ilike('%'+query+'%'), Filedbentity.previous_file_name.ilike('%'+query+'%'))).order_by(Filedbentity.display_name).all():        
            data.append({ 'display_name': x.display_name,
                          'previous_file_name': x.previous_file_name,
                          'sgdid': x.sgdid,
                          'is_in_browser': x.is_in_browser,
                          'is_in_spell': x.is_in_spell,
                          'is_public': x.is_public,
                          'year': x.year,
                          's3_url': x.s3_url,
                          'description': x.description })
        return HTTPOk(body=json.dumps(data),content_type='text/json')
    except Exception as e:
        log.error(e)
        return HTTPBadRequest(body=json.dumps({'error': str(e)}))
    finally:
        if DBSession:
            DBSession.remove()    

def add_metadata(request, old_file_id, uploaded_file):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])
        sgd = DBSession.query(Source).filter_by(display_name='SGD').one_or_none()                           
        source_id = sgd.source_id
        display_name = request.params.get('display_name')
        if display_name == '':
            return HTTPBadRequest(body=json.dumps({'error': "File display_name field is blank"}), content_type='text/json')
        success_message = ""




        
        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'metadata': "METADATA"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()
        
def update_metadata(request):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])

        sgdid = request.params.get('sgdid')
        if sgdid == '':
            return HTTPBadRequest(body=json.dumps({'error': "No SGDID is passed in."}), content_type='text/json')
    
        d = curator_session.query(Filedbentity).filter_by(sgdid=sgdid).one_or_none()

        if d is None:
            return HTTPBadRequest(body=json.dumps({'error': "The SGDID " + sgdid + " is not in the database."}), content_type='text/json')

        file_id = d.dbentity_id

        file_to_s3 = request.params.get('file_to_upload', '')

        if file_to_s3 != '':
            file_to_s3 = list(file_to_s3)[0]
            return HTTPBadRequest(body=json.dumps({'error': "file to load= " + str(file_to_s3)}), content_type='text/json')

        ## update file display_name
        
        display_name = request.params.get('display_name')
        if display_name == '':
            return HTTPBadRequest(body=json.dumps({'error': "File display_name field is blank"}), content_type='text/json')

        success_message = ""
        if display_name != d.display_name:
            success_message = "The file display name has been updated from '" + d.display_name + "' to '" + display_name + "'."
            d.display_name = display_name
            curator_session.add(d)



            
    
            
        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'metadata': "METADATA"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()


    
    
