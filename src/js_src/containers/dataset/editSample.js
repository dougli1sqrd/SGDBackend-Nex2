import React, { Component } from 'react';
import PropTypes from 'prop-types';
import CurateLayout from '../curateHome/layout';
import { setSample } from '../../actions/datasetSampleActions';  
import fetchData from '../../lib/fetchData';
import SampleSection from './sampleSection';
import { setError, setMessage } from '../../actions/metaActions';

const GET_DATASET = '/get_dataset_data';
const UPDATE_SAMPLE = '/datasetsample_update';
const DELETE_SAMPLE = '/datasetsample_delete';

const TIMEOUT = 300000;

class EditSample extends Component {
  constructor(props) {
    super(props);
    this.state = {
      samples: []
    };
    this.handleUpdateSubmit = this.handleUpdateSubmit.bind(this);
    this.handleDeleteSubmit = this.handleDeleteSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }

  componentDidMount() {
    let url = this.setVariables();
    this.getData(url);
    this.addEmptyRow();
  }

  getData(url) {
    fetchData(url).then( (data) => {
      this.setState({ samples: data['samples'] });
    })
    .catch(err => this.props.dispatch(setError(err.error)));
  }

  addEmptyRow() {
    let samples = this.state.samples;
    samples.push({ 'dbxref_id': '',
                   'display_name': '',
                   'strain_name': '',
                   'sample_order': '',
                   'description': '',
                   'dbxref_type': '',
                   'dbxref_url': '',
                   'taxonomy_id': '',
                   'biosample': '',
                   'format_name': '',
                   'obj_url': '' })
    this.setState({ samples: samples });
  }
    
  setVariables() {
    let urlList = window.location.href.split('/');
    let format_name = urlList[urlList.length-1];
    return GET_DATASET + '/' + format_name;
  }

  handleChange() {
    let currentSample = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentSample[key[0]] = key[1];
    }
    this.props.dispatch(setSample(currentSample));
  }
    
  handleUpdateSubmit(e) {
    this.updateData(e, UPDATE_SAMPLE);
  }

  handleDeleteSubmit(e) {
    this.deleteData(e, DELETE_SAMPLE);
  }

  updateData(formData, update_url) {
    fetchData(update_url, {
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
    
  sampleSections() {
    let sections = this.state.samples.map((sample, i) => {
      return (<SampleSection sample={sample} index={i} onUpdateSubmit={this.handleUpdateSubmit} onDeleteSubmit={this.handleDeleteSubmit} onOptionChange={this.handleChange} />);
    });
    return sections;
  }
    
  render() {
    return (
      <CurateLayout>
        <h2>Update Dataset Sample</h2>
        { this.sampleSections() }
      </CurateLayout>
    );
  }

}

EditSample.propTypes = {
  dispatch: PropTypes.func,
};

export default EditSample;
