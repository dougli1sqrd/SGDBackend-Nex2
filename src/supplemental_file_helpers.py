import logging
import os
import datetime
from sqlalchemy import or_
from pyramid.httpexceptions import HTTPBadRequest, HTTPOk
from sqlalchemy.exc import IntegrityError, DataError
import transaction
import json
from src.models import DBSession, Dbentity, Filedbentity, Referencedbentity, FilePath, \
                       Path, ReferenceFile, Source, Edam
from src.aws_helpers import get_checksum
from src.aws_helpers import upload_file_to_s3
from src.curation_helpers import get_curator_session

# PREVIEW_URL = os.environ['PREVIEW_URL']

log = logging.getLogger('curation')

FILE_TYPE = 'Supplemental'
DESC = 'Supplemental Materials'
PATH = '/supplemental_data'
FILE_EXTENSION = 'zip'
DBENTITY_STATUS = 'Active'
IS_PUBLIC = '1',
IS_IN_SPELL = '0'
IS_IN_BROWSER = '0'

def add_metadata_upload_files(request):

    return "HELLO WORLD"
