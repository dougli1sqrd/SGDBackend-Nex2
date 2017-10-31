from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden, HTTPOk, HTTPNotFound, HTTPFound
from pyramid.view import view_config
from pyramid.session import check_csrf_token
from sqlalchemy import create_engine
from sqlalchemy.orm.session import make_transient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker
from oauth2client import client, crypt
import logging
import os
import traceback
import transaction
import json

from .helpers import allowed_file, extract_id_request, secure_save_file, curator_or_none, extract_references, extract_keywords, get_or_create_filepath, extract_topic, extract_format, file_already_uploaded, link_references_to_file, link_keywords_to_file, FILE_EXTENSIONS, get_locus_by_id, get_go_by_id, refresh_homepage_cache
from .curation_helpers import process_pmid_list, get_curator_session, get_pusher_client
from .loading.promote_reference_triage import add_paper
from .models import DBSession, Dbentity, Dbuser, Referencedbentity, Straindbentity, Literatureannotation, Referencetriage, Referencedeleted, Locusdbentity, CurationReference, Locussummary, validate_tags
from .tsv_parser import parse_tsv_annotations

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
log = logging.getLogger()

def authenticate(view_callable):
    def inner(context, request):
        if 'email' not in request.session or 'username' not in request.session:
            return HTTPForbidden()
        else:
            return view_callable(request)
    return inner

@view_config(route_name='account', request_method='GET', renderer='json')
@authenticate
def account(request):
    return { 'username': request.session['username'] }

@view_config(route_name='get_locus_curate', request_method='GET', renderer='json')
@authenticate
def get_locus_curate(request):
    id = extract_id_request(request, 'locus', param_name="sgdid")
    locus = get_locus_by_id(id)
    return locus.get_summary_dict()

@view_config(route_name='locus_curate_update', request_method='PUT', renderer='json')
@authenticate
def locus_curate_update(request):
    try:
        id = extract_id_request(request, 'locus', param_name="sgdid")
        locus = get_locus_by_id(id)
        new_phenotype_summary = request.params.get('phenotype_summary')
        new_regulation_summary = request.params.get('regulation_summary')
        new_regulation_pmids = process_pmid_list(request.params.get('regulation_summary_pmids'))
        if len(new_phenotype_summary):
            locus.update_summary('Phenotype', request.session['username'], new_phenotype_summary)
        locus = get_locus_by_id(id)
        if len(new_regulation_summary):
            locus.update_summary('Regulation', request.session['username'], new_regulation_summary, new_regulation_pmids)
        locus = get_locus_by_id(id)
        pusher = get_pusher_client()
        pusher.trigger('sgd', 'curateHomeUpdate', {})
        return locus.get_summary_dict()
    except ValueError as e:
        return HTTPBadRequest(body=json.dumps({ 'error': str(e) }), content_type='text/json')

@view_config(route_name='reference_triage_id_delete', renderer='json', request_method='DELETE')
@authenticate
def reference_triage_id_delete(request):
    id = request.matchdict['id'].upper()
    triage = DBSession.query(Referencetriage).filter_by(curation_id=id).one_or_none()
    if triage:
        try:
            curator_session = get_curator_session(request.session['username'])
            triage = curator_session.query(Referencetriage).filter_by(curation_id=id).one_or_none()
            reference_deleted = Referencedeleted(pmid=triage.pmid, sgdid=None, reason_deleted='This paper was discarded during literature triage.', created_by=request.session['username'])
            curator_session.add(reference_deleted)
            curator_session.delete(triage)        
            transaction.commit()
            pusher = get_pusher_client()
            pusher.trigger('sgd', 'triageUpdate', {})
            return HTTPOk()
        except:
            traceback.print_exc()
            curator_session.rollback()
            return HTTPBadRequest(body=json.dumps({'error': 'DB failure. Verify that PMID is valid and not already present in SGD.'}))
        finally:
            curator_session.close()
    else:
        return HTTPNotFound()

@view_config(route_name='reference_triage_id', renderer='json', request_method='GET')
@authenticate
def reference_triage_id(request):
    id = request.matchdict['id'].upper()
    triage = DBSession.query(Referencetriage).filter_by(curation_id=id).one_or_none()
    if triage:
        return triage.to_dict()
    else:
        return HTTPNotFound()

@view_config(route_name='reference_triage_id_update', renderer='json', request_method='PUT')
@authenticate
def reference_triage_id_update(request):
    id = request.matchdict['id'].upper()
    triage = DBSession.query(Referencetriage).filter_by(curation_id=id).one_or_none()
    if triage:
        try:
            triage.update_from_json(request.json)
            transaction.commit()
        except:
            traceback.print_exc()
            DBSession.rollback()
            return HTTPBadRequest(body=json.dumps({'error': 'DB failure. Verify if pmid is valid and not already present.'}))
        pusher = get_pusher_client()
        pusher.trigger('sgd', 'triageUpdate', {})
        return HTTPOk()
    else:
        return HTTPNotFound()

@view_config(route_name='reference_triage_promote', renderer='json', request_method='PUT')
@authenticate
def reference_triage_promote(request):
    tags = request.json['tags']
    username = request.session['username']
    # validate tags before doing anything else
    try:
        validate_tags(tags)
    except Exception, e:
        return HTTPBadRequest(body=json.dumps({'error': str(e) }))
    id = request.matchdict['id'].upper()
    triage = DBSession.query(Referencetriage).filter_by(curation_id=id).one_or_none()
    new_reference_id = None
    if triage:
        # promote
        try:
            new_reference = add_paper(triage.pmid, request.json['data']['assignee'])
            new_reference_id = new_reference.dbentity_id
            DBSession.delete(triage)
            transaction.commit()
        except IntegrityError as e:
            traceback.print_exc()
            DBSession.rollback()
            return HTTPBadRequest(body=json.dumps({'error': str(e) }))
        except:
            traceback.print_exc()
            return HTTPBadRequest(body=json.dumps({'error': 'Error importing PMID into the database. Verify that PMID is valid and not already present in SGD.'}))
        # update tags
        new_reference = DBSession.query(Referencedbentity).filter_by(dbentity_id=new_reference_id).one_or_none()
        make_transient(new_reference)
        new_reference.update_tags(tags, username)
        pusher = get_pusher_client()
        pusher.trigger('sgd', 'triageUpdate', {})
        pusher.trigger('sgd', 'curateHomeUpdate', {})
        return new_reference.annotations_summary_to_dict()
    else:
        return HTTPNotFound()

@view_config(route_name='reference_triage_index', renderer='json', request_method='GET')
@authenticate
def reference_triage_index(request):
    triages = DBSession.query(Referencetriage).order_by(Referencetriage.date_created.asc()).all()
    return {'entries': [t.to_dict() for t in triages]}

@view_config(route_name='refresh_homepage_cache', request_method='POST', renderer='json')
@authenticate
def refresh_homepage_cache(request):
    refresh_homepage_cache()
    return True

@view_config(route_name='db_sign_in', request_method='POST', renderer='json')
def db_sign_in(request):
    if not check_csrf_token(request, raises=False):
        return HTTPBadRequest(body=json.dumps({'error':'Bad CSRF Token'}))
    try:
        username = request.params.get('username').lower()
        password = request.params.get('password')
        # create custom DB URI, replacing with username and password
        default_db_uri = os.environ['NEX2_URI']
        user_str = username + ':' + password + '@'
        user_db_uri = 'postgresql://' + user_str + default_db_uri.split('@')[1]
        temp_engine = create_engine(user_db_uri)
        session_factory = sessionmaker(bind=temp_engine)
        Temp_session = scoped_session(session_factory)
        user = Temp_session.query(Dbuser).filter_by(username=username.upper()).one_or_none()
        if user is None:
            raise ValueError('Invalid login')
        curator = curator_or_none(user.email)
        if curator is None:
            return HTTPForbidden(body=json.dumps({'error': 'User is not authorized on SGD'}))
        session = request.session
        session['email'] = curator.email
        session['username'] = curator.username
        log.info('User ' + curator.email + ' was successfuly authenticated.')
        return { 'username': session['username'] }
    except:
        traceback.print_exc()
        return HTTPForbidden(body=json.dumps({'error': 'Incorrect login details.'}))
    finally:
        if Temp_session:
            Temp_session.close()

@view_config(route_name='sign_in', request_method='POST', renderer='json')
def sign_in(request):
    if not check_csrf_token(request, raises=False):
        return HTTPBadRequest(body=json.dumps({'error':'Bad CSRF Token'}))

    if request.json_body['google_token'] is None:
        return HTTPForbidden(body=json.dumps({'error': 'Expected authentication token not found'}))
    
    try:
        idinfo = client.verify_id_token(request.json_body['google_token'], os.environ['GOOGLE_CLIENT_ID'])

        if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
            return HTTPForbidden(body=json.dumps({'error': 'Authentication token has an invalid ISS'}))
        
        if idinfo.get('email') is None:
            return HTTPForbidden(body=json.dumps({'error': 'Authentication token has no email'}))

        log.info('User ' + idinfo['email'] + ' trying to authenticate from ' + (request.remote_addr or '(no remote address)'))

        curator = curator_or_none(idinfo['email'])

        if curator is None:
            return HTTPForbidden(body=json.dumps({'error': 'User ' + idinfo['email'] + ' is not authorized on SGD'}))
        
        session = request.session

        if 'email' not in session:
            session['email'] = curator.email

        if 'username' not in session:
            session['username'] = curator.username

        log.info('User ' + idinfo['email'] + ' was successfuly authenticated.')

        return {'username': curator.username}
    except crypt.AppIdentityError:
        return HTTPForbidden(body=json.dumps({'error': 'Authentication token is invalid'}))

@view_config(route_name='sign_out', request_method='GET')
def sign_out(request):
    request.session.invalidate()
    return HTTPOk()

@view_config(route_name='reference_tags', renderer='json', request_method='GET')
@authenticate
def reference_tags(request):
    id = extract_id_request(request, 'reference', 'id', True)
    if id:
        reference = DBSession.query(Referencedbentity).filter_by(dbentity_id=id).one_or_none()
    else:
        reference = DBSession.query(Referencedbentity).filter_by(sgdid=request.matchdict['id']).one_or_none()
    return reference.get_tags()

@view_config(route_name='update_reference_tags', renderer='json', request_method='PUT')
@authenticate
def update_reference_tags(request):
    try:
        id = extract_id_request(request, 'reference', 'id', True)
        tags = request.json['tags']
        username = request.session['username']
        if id:
            reference = DBSession.query(Referencedbentity).filter_by(dbentity_id=id).one_or_none()
        else:
            reference = DBSession.query(Referencedbentity).filter_by(sgdid=request.matchdict['id']).one_or_none()
        make_transient(reference)
        reference.update_tags(tags, username)
        return reference.get_tags()
    except Exception, e:
        traceback.print_exc()
        return HTTPBadRequest(body=json.dumps({ 'error': str(e) }), content_type='text/json')

@view_config(route_name='get_recent_annotations', request_method='GET', renderer='json')
@authenticate
def get_recent_annotations(request):
    limit = 25
    annotations = []
    recent_summaries = DBSession.query(Locussummary).order_by(Locussummary.date_created.desc()).limit(limit).all()
    recent_literature = DBSession.query(Referencedbentity).order_by(Referencedbentity.dbentity_id.desc()).limit(limit).all()
    for d in recent_literature:
        annotations.append(d.annotations_summary_to_dict())
    for d in recent_summaries:
        annotations.append(d.to_dict())
    annotations = sorted(annotations, key=lambda r: r['date_created'], reverse=True)
    return annotations

@view_config(route_name='upload_spreadsheet', request_method='POST', renderer='json')
@authenticate
def upload_spreadsheet(request):
    try:
        tsv_file = request.POST['file'].file
        filename = request.POST['file'].filename
        template_type = request.POST['template']
        annotations = parse_tsv_annotations(DBSession, tsv_file, filename, template_type, request.session['username'])
        pusher = get_pusher_client()
        pusher.trigger('sgd', 'curateHomeUpdate', {})
        return {'annotations': annotations}
    except ValueError as e:
        return HTTPBadRequest(body=json.dumps({ 'error': str(e) }), content_type='text/json')
    except AttributeError:
        traceback.print_exc()
        return HTTPBadRequest(body=json.dumps({ 'error': 'Please attach a valid TSV file.' }), content_type='text/json')
    except:
        traceback.print_exc()
        return HTTPBadRequest(body=json.dumps({ 'error': 'Unable to process file upload. Please try again.' }), content_type='text/json')

# @view_config(route_name='upload', request_method='POST', renderer='json')
# @authenticate
# def upload_file(request):
#     keys = ['file', 'old_filepath', 'new_filepath', 'previous_file_name', 'display_name', 'status', 'topic_id', 'format_id', 'extension', 'file_date', 'readme_name', 'pmids', 'keyword_ids']
#     optional_keys = ['is_public', 'for_spell', 'for_browser']
    
#     for k in keys:
#         if request.POST.get(k) is None:
#             return HTTPBadRequest(body=json.dumps({'error': 'Field \'' + k + '\' is missing'}))

#     file = request.POST['file'].file
#     filename = request.POST['file'].filename

#     if not file:
#         log.info('No file was sent.')
#         return HTTPBadRequest(body=json.dumps({'error': 'No file was sent.'}))

#     if not allowed_file(filename):
#         log.info('Upload error: File ' + request.POST.get('display_name') + ' has an invalid extension.')
#         return HTTPBadRequest(body=json.dumps({'error': 'File extension is invalid'}))
    
#     try:
#         references = extract_references(request)
#         keywords = extract_keywords(request)
#         topic = extract_topic(request)
#         format = extract_format(request)
#         filepath = get_or_create_filepath(request)
#     except HTTPBadRequest as bad_request:
#         return HTTPBadRequest(body=json.dumps({'error': str(bad_request.detail)}))

#     if file_already_uploaded(request):
#         return HTTPBadRequest(body=json.dumps({'error': 'Upload error: File ' + request.POST.get('display_name') + ' already exists.'}))

#     fdb = Filedbentity(
#         # Filedbentity params
#         md5sum=None,
#         previous_file_name=request.POST.get('previous_file_name'),
#         topic_id=topic.edam_id,
#         format_id=format.edam_id,
#         file_date=datetime.datetime.strptime(request.POST.get('file_date'), '%Y-%m-%d %H:%M:%S'),
#         is_public=request.POST.get('is_public', 0),
#         is_in_spell=request.POST.get('for_spell', 0),
#         is_in_browser=request.POST.get('for_browser', 0),
#         filepath_id=filepath.filepath_id,
#         file_extension=request.POST.get('extension'),        

#         # DBentity params
#         format_name=request.POST.get('display_name'),
#         display_name=request.POST.get('display_name'),
#         s3_url=None,
#         source_id=339,
#         dbentity_status=request.POST.get('status')
#     )

#     DBSession.add(fdb)
#     DBSession.flush()
#     DBSession.refresh(fdb)

#     link_references_to_file(references, fdb.dbentity_id)
#     link_keywords_to_file(keywords, fdb.dbentity_id)
    
#     # fdb object gets expired after transaction commit
#     fdb_sgdid = fdb.sgdid
#     fdb_file_extension = fdb.file_extension
    
#     transaction.commit() # this commit must be synchronous because the upload_to_s3 task expects the row in the DB
#     log.info('File ' + request.POST.get('display_name') + ' was successfully uploaded.')
#     return Response({'success': True})
