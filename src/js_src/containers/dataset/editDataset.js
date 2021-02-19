import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import Loader from '../../components/loader';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import { setDataset } from '../../actions/datasetActions';
import { PREVIEW_URL } from '../../constants.js';
import OneDataset from './oneDataset';
const UPDATE_DATASET = '/dataset_update';
const GET_DATASET = '/get_dataset_data';

const TIMEOUT = 300000;

class EditDataset extends Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleUpdate = this.handleUpdate.bind(this);
  
    this.state = {
      dataset_id: null,
      format_name: null,
      preview_url: null,
      sample_url: null,
      track_url: null,
      isLoading: false,
      isComplete: false,
    };
  }

  componentDidMount() {
    let url = this.setVariables();
    this.getData(url);
  }

  handleChange() {
    let currentDataset = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentDataset[key[0]] = key[1];
    }
    this.props.dispatch(setDataset(currentDataset));
  }

  handleUpdate(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.dataset){
      formData.append(key,this.props.dataset[key]);
    }
    fetchData(UPDATE_DATASET, {
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
            <button type='submit' id='submit' value='0' className="button expanded" onClick={this.handleUpdate.bind(this)} > Update Dataset data </button>
          </div>
        </div>
      </div>
    );
  }

  getData(url) {
    this.setState({ isLoading: true });
    fetchData(url).then( (data) => {
      let currentDataset = {};
      for (let key in data) {
        currentDataset[key] = data[key];         
      }
      this.props.dispatch(setDataset(currentDataset));
    })
    .catch(err => this.props.dispatch(setError(err.error)))
    .finally(() => this.setState({ isComplete: true, isLoading: false }));
  }

  setVariables() {
    let urlList = window.location.href.split('/');
    let format_name = urlList[urlList.length-1];
    let url = GET_DATASET + '/' + format_name;  
    this.setState({
      format_name: format_name,
      preview_url: `${PREVIEW_URL}` + '/dataset/' + format_name,
      sample_url: '/#/curate/datasetsample/' + format_name,
      track_url: '/#/curate/datasettrack/' + format_name
    });
    return url;
  }

  links() {
    return (
      <div>
        <strong><a href={this.state.preview_url} target='preview'>Preview this Dataset Page</a> | <a href={this.state.sample_url} target='sample'>Update Dataset Sample(s)</a> | <a href={this.state.track_url} target='track'>Update Dataset Track(s)</a></strong>
      </div>
    );
  }

  displayForm() {
    return (
      <div>
        {this.links()}
        <hr />
        <form onSubmit={this.handleUpdate} ref='form'>
          <input name='format_name' value={this.props.dataset.format_name} className="hide" />
          <OneDataset dataset={this.props.dataset} onOptionChange={this.handleChange} />
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

EditDataset.propTypes = {
  dispatch: PropTypes.func,
  dataset: PropTypes.object
};


function mapStateToProps(state) {
  return {
    dataset: state.dataset['currentDataset']
  };
}

export default connect(mapStateToProps)(EditDataset);
