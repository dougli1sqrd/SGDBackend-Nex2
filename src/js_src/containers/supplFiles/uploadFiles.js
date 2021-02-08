import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import Loader from '../../components/loader';
import Dropzone from 'react-dropzone';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
// import { setSupplFile } from '../../actions/supplFileActions.js';
import style from '../fileMetadata/style.css';
const UPLOAD_FILES = '/upload_suppl_files';

const TIMEOUT = 300000;

class UploadFiles extends Component {
  constructor(props) {
    super(props);

    this.handleUpload = this.handleUpload.bind(this);
    this.renderFileDrop = this.renderFileDrop.bind(this);
      
    this.state = {
      files: [],
      isLoading: false,
      isComplete: false,
    };
  }
    
  handleClear(){
    this.setState({ files: [] });
  }

  handleDrop(files){
    this.setState({ files: files });
  }

  renderFileDrop() {
    if(this.state.files.length){
      let filenames = this.state.files.map( (file, index) => {
        return <li key={index}>{file.name}</li>;
      }); 
      return(
        <div>
          <ul>{filenames}</ul>
          <a onClick={this.handleClear.bind(this)}>Clear File(s)</a>
        </div>
      );
    }	
    return  (
      <div className='row'>
        <div className='columns medium-6 small-6'>
          <Dropzone onDrop={this.handleDrop.bind(this)} multiple={true}>
            <p className={style.uploadMsg}>Drop file here or click to select.</p>
            <h3 className={style.uploadIcon}><i className='fa fa-cloud-upload' /></h3>
          </Dropzone>
        </div>
        <div className='columns medium-6 small-6'>Note: It will take a while to upload the files.
        </div>
      </div>);
  }
    
  handleUpload(e) {
    e.preventDefault();
    let formData = new FormData();
    formData.append('files', this.state.files);
    fetchData(UPLOAD_FILES, {
      type: 'POST',
      credentials: 'same-origin',
      headers: {
        'X-CSRF-Token': this.props.csrfToken
      },
      data: formData,
      processData: false,
      contentType: false,
      timeout: TIMEOUT
    }).then((data) => {
      this.props.dispatch(setMessage(data.success));
    }).catch( (data) => {
      let errorMessage = data ? data.error: 'Error occured: connection timed out';
      this.props.dispatch(setError(errorMessage));
      this.setState({ isPending: false});
    });
  }

  addButton() {
    return (
      <div>
        <div className='row'>
          <div className='columns medium-6 small-6'>
            <button type='submit' id='submit' value='0' className="button expanded" onClick={this.handleUpload.bind(this)} > Upload Files </button>
          </div>
        </div>
      </div>
    );
  }

  displayForm() {
    return (
      <div>
        <form onSubmit={this.handleUpload} ref='form'>
          {this.renderFileDrop()}
          <hr />
          {this.addButton()}          	
        </form>
      </div>
    );
  }

  render() {
    if (this.state.isLoading) {
      return (
        <div>
          <div>Please wait while we are constructing the update form.</div>
          <div><Loader /></div>
        </div>
      );
    }
    if (this.state.isComplete) {
      return this.displayForm();
    }
    else {
      return (<div>Something is wrong while we are constructing the update form.</div>);
    }
  }
}

UploadFiles.propTypes = {
  dispatch: PropTypes.func,
  csrfToken: PropTypes.string
};


function mapStateToProps(state) {
  return {
    csrfToken: state.auth.get('csrfToken')
  };
}

export default connect(mapStateToProps)(UploadFiles);
