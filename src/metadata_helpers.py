import logging
import os
from sqlalchemy import or_
from pyramid.httpexceptions import HTTPBadRequest, HTTPOk
from sqlalchemy.exc import IntegrityError, DataError
import transaction
import json
from src.models import DBSession, Dbentity, Filedbentity, FilePath, Path,\
                       FileKeyword, Keyword, Source
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

def insert_file_path(curator_session, CREATED_BY, source_id, file_id, path_id):

    try:
        x = FilePath(file_id = file_id,
                     path_id = path_id,
                     source_id = source_id,
                     created_by = CREATED_BY)
        curator_session.add(x)
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        
def insert_file_keyword(curator_session, CREATED_BY, source_id, file_id, keyword_id):

    try:
        x = FileKeyword(file_id = file_id,
                        keyword_id = keyword_id,
                        source_id = source_id,
                        created_by = CREATED_BY)
        curator_session.add(x)
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
            
def insert_keyword(curator_session, CREATED_BY, source_id, keyword):

    kw = curator_session.query(Keyword).filter(Keyword.display_name.ilike(keyword)).one_or_none()
    if kw:
        return kw.keyword_id

    keyword_id = None
    returnValue = None
    keyword_id = None
    try:
        format_name = keyword.replace(' ', '_').replace('/', '_')
        obj_url = '/keyword/' + format_name
        x = Keyword(format_name = format_name,
                    display_name = keyword,
                    obj_url = obj_url,
                    source_id = source_id,
                    is_obsolete = '0',
                    created_by = CREATED_BY)
        curator_session.add(x)
        transaction.commit()
        keyword_id = x.keyword_id
    except Exception as e:
        transaction.abort()
        if curator_session:
            curator_session.rollback()
        returnValue = 'Insert Keyword failed: ' + str(e)
    if keyword_id:
        return keyword_id 
    else:
        return returnValue
    
def add_metadata(request, source_id, old_file_id, uploaded_file):

    try:
        CREATED_BY = request.session['username']
        curator_session = get_curator_session(request.session['username'])
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
        sgd = DBSession.query(Source).filter_by(display_name='SGD').one_or_none()
        source_id = sgd.source_id
        
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

        success_message = ""
        
        ## update file display_name
        display_name = request.params.get('display_name')
        if display_name == '':
            return HTTPBadRequest(body=json.dumps({'error': "File display_name field is blank"}), content_type='text/json')
        if display_name != d.display_name:
            success_message = "display_name has been updated from '" + d.display_name + "' to '" + display_name + "'."
            d.display_name = display_name
            curator_session.add(d)

        ## update dbentity_status
        dbentity_status = request.params.get('dbentity_status', None)
        if dbentity_status is None:
            return HTTPBadRequest(body=json.dumps({'error': "dbentity_status field is blank"}), content_type='text/json')
        if dbentity_status not in ['Active', 'Archived']:
            return HTTPBadRequest(body=json.dumps({'error': "dbentity_status must be 'Active' or 'Archived'."}), content_type='text/json')
        if dbentity_status != d.dbentity_status:
            success_message = success_message + "<br>dbentity_status has been updated from '" + d.dbentity_status + "' to '" + dbentity_status + "'."
            d.dbentity_status = dbentity_status
            curator_session.add(d)
        
        ## update previous file names
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
        is_public = request.params.get('is_public', '')
        if is_public == '':
            return HTTPBadRequest(body=json.dumps({'error': "is_public field is blank"}), content_type='text/json')
        is_public = True if is_public == 'true' else False
        if is_public != d.is_public:
            success_message = success_message + "<br>is_public has been updated from '" + str(d.is_public) + "' to '" + str(is_public) + "'."
            d.is_public = is_public
            
        ## update is_in_spell (required field)
        is_in_spell = request.params.get('is_in_spell', '')
        if is_in_spell == '':
            return HTTPBadRequest(body=json.dumps({'error': "is_in_spell field is blank"}), content_type='text/json')
        is_in_spell = True if is_in_spell == 'true' else False
        if is_in_spell != d.is_in_spell:
            success_message = success_message + "<br>is_in_spell has been updated from '" + str(d.is_in_spell) + "' to '" + str(is_in_spell) + "'."
            d.is_in_spell = is_in_spell

        ## update is_in_browser (required field)
        is_in_browser = request.params.get('is_in_browser', '')
        if is_in_browser == '':
            return HTTPBadRequest(body=json.dumps({'error': "is_in_browser field is blank"}), content_type='text/json')
        is_in_browser = True if is_in_browser == 'true' else False
        if is_in_browser != d.is_in_browser:
            success_message = success_message + "<br>is_in_browser has been updated from '" + str(d.is_in_browser) + "' to '" + str(is_in_browser) + "'."
            d.is_in_browser = is_in_browser
        
        ## update file_date (required field)  
        file_date = request.params.get('file_date', '')
        if file_date == '':
            return HTTPBadRequest(body=json.dumps({'error': "file_date field is blank"}), content_type='text/json')
        if '-' not in file_date:
            return HTTPBadRequest(body=json.dumps({'error': "file_date format: yyyy-mm-dd"}), content_type='text/json')
        file_date_db = str(d.file_date).split(' ')[0]
        if file_date != file_date_db:    
            success_message = success_message + "<br>file_date has been updated from '" + file_date_db + "' to '" + file_date + "'."
            d.file_date = file_date
            
        ## update readme_file_id (optional field)
        readme_file_id = request.params.get('readme_file_id', None)
        changed = 0
        if readme_file_id is not None:
            if str(readme_file_id).isdigit():
                readme_file_id = int(readme_file_id)
                if not d.readme_file_id or readme_file_id != d.readme_file_id:
                    changed = 1
        elif d.readme_file_id:
            changed = 1
        if changed == 1:
            success_message = success_message + "<br>readme_file_id has been updated from '" + str(d.readme_file_id) + "' to '" + str(readme_file_id) + "'."
            d.readme_file_id = readme_file_id
        curator_session.add(d)
                    
        ## update path_id (path)
        path_id = request.params.get('path_id', None)
        fp = curator_session.query(FilePath).filter_by(file_id=file_id).one_or_none()
        if fp is None and path_id:
            insert_file_path(curator_session, CREATED_BY, source_id, file_id, int(path_id))
    
        ## update keyword(s)
        all_kw = curator_session.query(FileKeyword).filter_by(file_id=file_id).all()
        keywords_db = {}
        for kw in all_kw:
            keywords_db[kw.keyword.display_name.upper()] = kw.keyword_id
        keywords = request.params.get('keywords', '')
        kw_list = keywords.split('|')
    
        for kw in kw_list:
            kw = kw.strip()
            if kw.upper() in keywords_db:
                del keywords_db[kw.upper()]
                continue
            keyword_id = insert_keyword(curator_session, CREATED_BY, source_id, kw)
            if str(keyword_id).isdigit():
                insert_file_keyword(curator_session, CREATED_BY, source_id, file_id, keyword_id)
            else:
                err_msg = keyword_id 
                return HTTPBadRequest(body=json.dumps({'error': err_msg}), content_type='text/json')
    
        for kw in keywords_db:
            keyword_id = keywords_db[kw]
            fk = curator_session.query(FileKeyword).filter_by(file_id=file_id, keyword_id=keyword_id).one_or_none()
            if fk:
                curator_session.delete(fk)

        if success_message == '':
            success_message = "Nothing changed"
            
        transaction.commit()
        return HTTPOk(body=json.dumps({'success': success_message, 'metadata': "METADATA"}), content_type='text/json')
    except Exception as e:
        return HTTPBadRequest(body=json.dumps({'error': str(e)}), content_type='text/json')
    finally:
        if curator_session:
            curator_session.remove()


    
    
