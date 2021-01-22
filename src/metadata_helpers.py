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

        file_name = request.params.get('file_name')

        if file_name:
            return HTTPBadRequest(body=json.dumps({'error': "NEW file to upload: file name = " + str(file_name)}), content_type='text/json')
    
        ## update file display_name
        display_name = request.params.get('display_name')
        if display_name == '':
            return HTTPBadRequest(body=json.dumps({'error': "File display_name field is blank"}), content_type='text/json')

        success_message = ""
        if display_name != d.display_name:
            success_message = "display_name has been updated from '" + d.display_name + "' to '" + display_name + "'."
            d.display_name = display_name
            curator_session.add(d)

        ## update previous file name
        previous_file_name = request.params.get('previous_file_name', '')
        if previous_file_name != d.previous_file_name:
            success_message = success_message + "<br>previous_file_name has been updated from '" + d.previous_file_name + "' to '" + previous_file_name + "'."
            d.previous_file_name = previous_file_name
            curator_session.add(d)

        ## update description
        description = request.params.get('description', '')
        if description != d.description:
            success_message = success_message + "<br>description has been updated from '" + d.description + "' to '" + description + "'."
            d.description = description
            curator_session.add(d)

        ## update year                                                                              
        year = request.params.get('year')
        if year is None:
            return HTTPBadRequest(body=json.dumps({'error': "year field is blank"}), content_type='text/json')
        year = int(year)
        if year != d.year:
            success_message = success_message + "<br>year has been updated from '" + str(d.year) + "' to '" + str(year) + "'."
            d.year = year
            curator_session.add(d)    

        ## update file_size 
        file_size = request.params.get('file_size')
        if file_size is None:
            return HTTPBadRequest(body=json.dumps({'error': "file_size field is blank"}), content_type='text/json')
        file_size = int(file_size)
        if file_size != d.file_size:
            success_message = success_message + "<br>file_size has been updated from '" + str(d.file_size) + "' to '" + str(file_size) + "'."
            d.file_size = file_size
            curator_session.add(d)

        ## update file_extension
        file_extension = request.params.get('file_extension')
        if file_extension is None:
            return HTTPBadRequest(body=json.dumps({'error': "file_extension field is blank"}), content_type='text/json')
        if file_extension != d.file_extension:
            success_message = success_message + "<br>file_extension has been updated from '" + str(d.file_extension) + "' to '" + file_extension + "'."
            d.file_extension = file_extension
            curator_session.add(d)

        ## update topic_id (required field)
        topic_id = request.params.get('topic_id')
        topic_id = int(topic_id)
        if topic_id != d.topic_id:
            success_message = success_message + "<br>topic_id has been updated from '" + str(d.topic_id) + "' to '" + str(topic_id) + "'."
            d.topic_id = topic_id
            
        ## update data_id (required field)
        data_id = request.params.get('data_id')
        data_id = int(data_id)
        if data_id != d.data_id:
            success_message = success_message + "<br>data_id has been updated from '" + str(d.data_id) + "' to '" + str(data_id) + "'."
            d.data_id = data_id
            
        ## update format_id (required field)
        format_id = request.params.get('format_id')
        format_id = int(format_id)
        if format_id != d.format_id:
            success_message = success_message + "<br>format_id has been updated from '" + str(d.format_id) + "' to '" + str(format_id) + "'."
            d.format_id = format_id
            
        ## update is_public (required field)
        is_public = request.params.get('is_public')                                                                                            
        if is_public == 'true':
            is_public = True
        else:
            is_public = False
        changed = 0
        if is_public != d.is_public:
            changed = 1
            
        
        ## update is_in_spell (required field)
        ## update is_in_browser (required field)

        ## update file_date (required field)  

        ## update readme_file_id (optional field)
        ## json??

        ## update keyword(s)
        ## update path_id (path)
        
        
        return HTTPBadRequest(body=json.dumps({'error': "OK=" + str(changed)}), content_type='text/json')
    
        

        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'metadata': "METADATA"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()


    
    
