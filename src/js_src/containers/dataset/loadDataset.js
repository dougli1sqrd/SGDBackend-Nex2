import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import Dropzone from 'react-dropzone';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import style from '../fileMetadata/style.css';
const LOAD_DATASET = '/dataset_load';
const LOAD_SAMPLE = '/datasetsample_load';

const TIMEOUT = 300000;

class LoadDataset extends Component {
  constructor(props) {
    super(props);

    this.handleUpload = this.handleUpload.bind(this);
    this.renderFileDrop = this.renderFileDrop.bind(this);
    this.handleToggleDatasetOrSample = this.handleToggleDatasetOrSample.bind(this);

    this.state = {
      files: [],
      isDataset: true 
    };
  }

  handleToggleDatasetOrSample() {
    this.setState({ isDataset: !this.state.isDataset });
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
        <div className='row'>
          <div>
            <ul>{filenames}</ul>
            <a onClick={this.handleClear.bind(this)}>Clear File(s)</a>
          </div>
          <div><strong>It will take a while to load data into database...</strong></div>
        </div>
      );
    }	
    return  (
      <div className='row'>
        <div className='columns medium-4 small-4'>
          <Dropzone onDrop={this.handleDrop.bind(this)} multiple={true}>
            <p className={style.uploadMsg}>Drop file here or click to select.</p>
            <h3 className={style.uploadIcon}><i className='fa fa-cloud-upload' /></h3>
          </Dropzone>
        </div>
        <div className='columns medium-8 small-8'>
          {this.note()}
        </div>
      </div>);
  }
    
  handleUpload(e) {
    e.preventDefault();
    let load_url = LOAD_SAMPLE;
    if (this.state.isDataset) {
      load_url = LOAD_DATASET;
    }
    let success_message = '';
    let error_message = '';
    this.state.files.map( (file, index) => {
      console.log('uploading file: ' + index + ' ' + file.name);
      let formData = new FormData();
      formData.append('file', file);
      fetchData(load_url, {
        type: 'POST',
        credentials: 'same-origin',
        headers: {
          'X-CSRF-Token': this.props.csrfToken,
        },
        // contentType: file.type,
        data: formData,
        processData: false,
        contentType: false,
        timeout: TIMEOUT
      }).then((data) => {
        success_message = success_message + data.success;
        this.props.dispatch(setMessage(success_message));
      }).catch( (data) => {
        let errorMessage = data ? data.error: 'Error occured: connection timed out';
        error_message = error_message + errorMessage;
        this.props.dispatch(setError(error_message));
      });
    });
  }

  note() {
    if (this.state.isDataset) {
      return (<div>Please upload one or more <strong>dataset</strong> file(s). </div>);
    }
    else {
      return (<div>Please upload one or more <strong>dataset sample</strong> file(s). </div>);
    }
  }

  buttonName() {
    if (this.state.isDataset) {
      return 'Load Dataset';
    }
    else {
      return 'Load Dataset Sample';
    }
  }
    
  addButton() {
    return (
      <div>
        <div className='row'>
          <div className='columns medium-6 small-6'>
            <button type='submit' id='submit' value='0' className="button expanded" onClick={this.handleUpload.bind(this)} > {this.buttonName()} </button>
          </div>
        </div>
      </div>
    );
  }
    
  displayForm() {
    return (
      <div>
        <div className='row'>
          <div className='columns medium-6 small-6'>
            <button type="button" className="button expanded" onClick={this.handleToggleDatasetOrSample} disabled={this.state.isDataset}>Load Dataset</button>
          </div>
          <div className='columns medium-6 small-6 end'>
            <button type="button" className="button expanded" onClick={this.handleToggleDatasetOrSample} disabled={!this.state.isDataset}>Load Dataset Sample</button>
          </div>
        </div>    
        <form onSubmit={this.handleUpload} ref='form'>
          {this.renderFileDrop()}
          <hr />
          {this.addButton()}
        </form>
      </div>
    );
  }

  render() {
    return this.displayForm();
  }
}

LoadDataset.propTypes = {
  dispatch: PropTypes.func,
  csrfToken: PropTypes.string
};


function mapStateToProps(state) {
  return {
    csrfToken: state.auth.get('csrfToken')
  };
}

export default connect(mapStateToProps)(LoadDataset);
