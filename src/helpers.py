from math import pi, sqrt, acos
import datetime
import hashlib
import werkzeug
import os
import pusher
import shutil
import string
import tempfile
import tinys3
import transaction
from pyramid.httpexceptions import HTTPForbidden, HTTPBadRequest
from .models import DBSession, Dbuser, Referencedbentity, Keyword, Filepath, Edam, Filedbentity, FileKeyword, ReferenceFile

import logging
log = logging.getLogger(__name__)

FILE_EXTENSIONS = ['bed', 'bedgraph', 'bw', 'cdt', 'chain', 'cod', 'csv', 'cusp', 'doc', 'docx', 'fsa', 'gb', 'gcg', 'gff', 'gif', 'gz', 'html', 'jpg', 'pcl', 'pdf', 'pl', 'png', 'pptx', 'README', 'sql', 'sqn', 'tgz', 'txt', 'vcf', 'wig', 'wrl', 'xls', 'xlsx', 'xml', 'sql', 'txt', 'html', 'gz', 'tsv']
S3_ACCESS_KEY = os.environ['S3_ACCESS_KEY']
S3_SECRET_KEY = os.environ['S3_SECRET_KEY']
S3_BUCKET = os.environ['S3_BUCKET']

def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), ""):
            hash.update(chunk)
    return hash.hexdigest()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in FILE_EXTENSIONS

def secure_save_file(file, filename):
    filename = werkzeug.secure_filename(filename)
    temp_file_path = os.path.join(tempfile.gettempdir(), filename)

    file.seek(0)
    with open(temp_file_path, 'wb') as output_file:
	shutil.copyfileobj(file, output_file)

    return temp_file_path

def curator_or_none(email):
    return DBSession.query(Dbuser).filter((Dbuser.email == email) & (Dbuser.status == 'Current')).one_or_none()

def authenticate(view_callable):
    def inner(context, request):
        if 'email' not in request.session or 'username' not in request.session:
            return HTTPForbidden()
        else:
            return view_callable(request)
    return inner

def extract_references(request):
    references = []
    if request.POST.get("pmids") != '':
        pmids = str(request.POST.get("pmids")).split(",")
        for pmid in pmids:
            try:
                f_pmid = float(pmid)
            except ValueError:
                log.info('Upload error: PMIDs must be integer numbers. Sent: ' + pmid)
                raise HTTPBadRequest('PMIDs must be integer numbers. You sent: ' + pmid)
            
            reference = DBSession.query(Referencedbentity).filter(Referencedbentity.pmid == f_pmid).one_or_none()
            if reference is None:
                log.info('Upload error: nonexistent PMID(s): ' + pmid)
                raise HTTPBadRequest('Nonexistent PMID(s): ' + pmid)
            else:
                references.append(reference.dbentity_id)
    return references

def extract_keywords(request):
    keywords = []
    if request.POST.get("keyword_ids") != '':
        keyword_ids = str(request.POST.get("keyword_ids")).split(",")
        for keyword_id in keyword_ids:
            keyword_obj = DBSession.query(Keyword).filter(Keyword.keyword_id == keyword_id).one_or_none()
            if keyword_obj is None:
                log.info('Upload error: invalid or nonexistent Keyword ID: ' + keyword_id)
                raise HTTPBadRequest('Invalid or nonexistent Keyword ID: ' + keyword_id)
            else:
                keywords.append(keyword_obj.keyword_id)
    return keywords

def get_or_create_filepath(request):
    filepath = DBSession.query(Filepath).filter(Filepath.filepath == request.POST.get("new_filepath")).one_or_none()

    if filepath is None:
        filepath = Filepath(filepath=request.POST.get("new_filepath"), source_id=339)
        DBSession.add(filepath)
        DBSession.flush()
        DBSession.refresh(filepath)
    return filepath

def extract_topic(request):
    topic = DBSession.query(Edam).filter(Edam.edam_id == request.POST.get("topic_id")).one_or_none()
    if topic is None:
        log.info('Upload error: Topic ID ' + request.POST.get("topic_id") + ' is not registered or is invalid.')
        raise HTTPBadRequest('Invalid or nonexistent Topic ID: ' + request.POST.get("topic_id"))
    return topic

def extract_format(request):
    format = DBSession.query(Edam).filter(Edam.edam_id == request.POST.get("format_id")).one_or_none()
    if format is None:
        log.info('Upload error: Format ID ' + request.POST.get("format_id") + ' is not registered or is invalid.')
        raise HTTPBadRequest('Invalid or nonexistent Format ID: ' + request.POST.get("format_id"))
    return format

def file_already_uploaded(request):
    fdb = DBSession.query(Filedbentity).filter(Filedbentity.format_name == request.POST.get("display_name")).one_or_none()
    if fdb is not None:
        log.info('Upload error: File ' + request.POST.get("display_name") + ' already exists.')
        return True
    return False

def get_pusher_client():
    pusher_client = pusher.Pusher(
        app_id=os.environ['PUSHER_APP_ID'],
        key=os.environ['PUSHER_KEY'],
        secret=os.environ['PUSHER_SECRET'],
        ssl=True
    )
    return pusher_client

def link_references_to_file(references, fdb_dbentity_id):
    for reference_id in references:
        rf = ReferenceFile(
            reference_id=reference_id,
            file_id=fdb_dbentity_id,
            source_id=339
        )
        DBSession.add(rf)
    DBSession.commit()

def link_keywords_to_file(keywords, fdb_dbentity_id):
    for keyword_id in keywords:
        fk = FileKeyword(
            keyword_id=keyword_id,
            file_id=fdb_dbentity_id,
            source_id=339
        )
        DBSession.add(fk)
    DBSession.commit()

def calc_venn_measurements(A, B, C):
    e = .01
    r = sqrt(1.0*A/pi)
    s = sqrt(1.0*B/pi)
    if A == C or B == C:
        return r, s, abs(r-s)-1
    elif C == 0:
        return r, s, r+s+1
    else:
        x = binary_search(C, lambda x: area_of_intersection(r, s, x), abs(r-s), r+s, e)
        return r, s, x
    
def binary_search(value, f, lower, upper, e, max_iter=None):
    midpoint = lower + 1.0*(upper-lower)/2
    value_at_midpoint = f(midpoint)

    if max_iter is not None:
        max_iter = max_iter - 1
        
    if abs(value_at_midpoint - value) < e or (max_iter is not None and max_iter == 0):
        return midpoint
    elif value > value_at_midpoint:
        return binary_search(value, f, lower, midpoint, e, max_iter)
    else:
        return binary_search(value, f, midpoint, upper, e, max_iter)

# creates Filedbentity, uploads to s3, and updates Filedbentity row with s3_url
def upload_file(username, file, **kwargs):
    filename = kwargs.get('filename')
    data_id = kwargs.get('data_id')
    topic_id = kwargs.get('topic_id')
    format_id = kwargs.get('format_id')
    is_public = kwargs.get('is_public', False)
    is_in_spell = kwargs.get('is_in_spell', False)
    is_in_browser = kwargs.get('is_in_browser', False)
    file_date = kwargs.get('file_date', datetime.datetime.now())
    year = kwargs.get('year', file_date.year)
    file_extension = kwargs.get('file_extension')
    display_name = kwargs.get('display_name')
    format_name = kwargs.get('format_name', display_name)
    source_id = kwargs.get('source_id', 834)
    status = kwargs.get('status', 'Active')
    description = kwargs.get('description', None)

    md5sum = hashlib.md5(file.getvalue()).hexdigest()
    fdb = Filedbentity(
        md5sum=md5sum,
        previous_file_name=filename,
        data_id=data_id,
        topic_id=topic_id,
        format_id=format_id,
        file_date=file_date,
        year=year,
        is_public=is_public,
        is_in_spell=is_in_spell,
        is_in_browser=is_in_browser,
        source_id=source_id,
        # filepath_id=filepath.filepath_id,
        file_extension=file_extension,
        format_name=format_name,
        display_name=display_name,
        s3_url=None,
        dbentity_status=status,
        description=description,
        subclass='FILE',
        created_by=username
    )
    DBSession.add(fdb)
    DBSession.flush()
    DBSession.refresh(fdb)
    # get s3_url and upload
    s3_url = fdb.sgdid + '/' + filename
    conn = tinys3.Connection(S3_ACCESS_KEY,S3_SECRET_KEY,tls=True)
    conn.upload(s3_url, file, S3_BUCKET)
    # update s3 url
    fdb.s3_url = s3_url
    DBSession.flush()
    transaction.commit()
    
def area_of_intersection(r, s, x):
    if x <= abs(r-s):
        return min(pi*pow(r, 2), pi*pow(s, 2))
    elif x > r+s:
        return 0
    else:
        return pow(r,2)*acos(1.0*(pow(x,2) + pow(r,2) - pow(s,2))/(2*x*r)) + pow(s,2)*acos(1.0*(pow(x,2) + pow(s,2) - pow(r,2))/(2*x*s)) - .5*sqrt((-x+r+s)*(x+r-s)*(x-r+s)*(x+r+s))

def link_gene_names(raw, locus_names_ids):
    # first create an object with display_name as key and sgdid as value
    locus_names_object = {}
    for d in locus_names_ids:
        display_name = d[0]
        sgdid = d[1]
        locus_names_object[display_name] = sgdid
    processed = raw
    words = raw.split(' ')
    for p_original_word in words:
        original_word = p_original_word.translate(None, string.punctuation)
        wupper = original_word.upper()
        if wupper in locus_names_object.keys():
            sgdid = locus_names_object[wupper]
            url = '/locus/'  + sgdid
            new_str = '<a href="' + url + '">' + wupper + '</a>'
            processed = processed.replace(original_word, new_str)
    return processed
