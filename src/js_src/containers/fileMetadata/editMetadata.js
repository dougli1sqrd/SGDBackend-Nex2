import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import Loader from '../../components/loader';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import { setFileMetadata } from '../../actions/fileMetadataActions';
// import { PREVIEW_URL } from '../../constants.js';
// import OneMetadata from './oneMetadata';
const UPDATE_METADATA = '/file_metadata_update';
const GET_METADATA = '/get_one_file_metadata';

const TIMEOUT = 300000;

class EditMetadata extends Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleUpdate = this.handleUpdate.bind(this);
    this.handleDelete = this.handleDelete.bind(this);
  
    this.state = {
      display_name: null,
      previous_file_name: null,
      s3_url: null,	
      isLoading: false,
      isComplete: false,
    };
  }

  componentDidMount() {
    let url = this.setVariables();
    this.getData(url);
  }

  handleChange() {
    let currentMetadata = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentMetadata[key[0]] = key[1];
    }
    this.props.dispatch(setFileMetadata(currentMetadata));
  }

  handleUpdate(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.metadata){
      formData.append(key,this.props.metadata[key]);
    }
    fetchData(UPDATE_METADATA, {
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      timeout: TIMEOUT
    }).then((data) => {
      this.props.dispatch(setMessage(data.success));
    }).catch((err) => {
      this.props.dispatch(setError(err.error));
    });
  }

  addButtons() {
    return (
      <div>
        <div className='row'>
          <div className='columns medium-6 small-6'>
            <button type='submit' id='submit' value='0' className="button expanded" onClick={this.handleUpdate.bind(this)} > Update File Metadata </button>
          </div>
        </div>
      </div>
    );
  }

  getData(url) {
    this.setState({ isLoading: true });
    fetchData(url).then( (data) => {
      let currentMetadata = {};
      for (let key in data) {
        currentMetadata[key] = data[key];
      }
      this.props.dispatch(setFileMetadata(currentMetadata));
    })
    .catch(err => this.props.dispatch(setError(err.error)))
    .finally(() => this.setState({ isComplete: true, isLoading: false }));
  }

  setVariables() {
    let urlList = window.location.href.split('/');
    let sgdid = urlList[urlList.length-1];
    let url = GET_METADATA + '/' + sgdid;  
    this.setState({
      sgdid: sgdid,
    });
    return url;
  }
    
  displayForm() {
    return (
      <div>
        <form onSubmit={this.handleUpdate} ref='form'>
          <input name='sgdid' value={this.state.sgdid} className="hide" />
          // <OneMetadata metadata={this.props.metadata} onOptionChange={this.handleChange} />
          {this.addButtons()}          	
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

EditMetadata.propTypes = {
  dispatch: PropTypes.func,
  metadata: PropTypes.object
};


function mapStateToProps(state) {
  return {
    metadata: state.metadata['currentMetadata']
  };
}

export default connect(mapStateToProps)(EditMetadata);
