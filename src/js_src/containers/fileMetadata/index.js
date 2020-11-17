/* eslint-disable no-unused-vars */
/**
 * @summary File Curation container component
 * @author fgondwe
 * Notes:
 *      user should be able to update a readmefile, comments for instance.
 *      update readmefile automatically with s3 urls.
 */
import React, {Component} from 'react';
import { connect } from 'react-redux';
import CurateLayout from '../curateHome/layout';
import fetchData from '../../lib/fetchData';
import { clearError, setError } from '../../actions/metaActions';
import LoadingPage from '../../components/loadingPage';
import PropTypes from 'prop-types';
import FileMetadataForm from '../../components/FileMetadata/fileMetadataForm';


import { Route, Redirect } from 'react-router';

const UPLOAD_URL = '/upload_file_curate';
const UPLOAD_TAR_URL = '/upload_tar_file';

const UPLOAD_TIMEOUT = 120000;
const DROP_DOWN_URL = '/file_curate_menus';

class FileMetadata extends Component {
  constructor(props){
    super(props);
    this.state = {
      files: [],
      isPending: false,
      toHome: false,
    };
  }

  render(){
    if(this.state.toHome){
      window.location.href = '/';
      return false;
    }
    else if(this.state.isPending){
      return ( <LoadingPage />);
    }
    else{
      return (
        <CurateLayout>
          <div>
            <FileMetadataForm fileData={{}} location={this.props.location} />
          </div>
        </CurateLayout>);
    }
  }

}

FileMetadata.propTypes = {
  csrfToken: PropTypes.string,
  dispatch: PropTypes.func,
  location: PropTypes.object
};

function mapStateToProps(state){
  return {
    csrfToken: state.auth.get('csrfToken')};
}

export { FileMetadata as FileMetadata };
export default connect(mapStateToProps)(FileMetadata);
