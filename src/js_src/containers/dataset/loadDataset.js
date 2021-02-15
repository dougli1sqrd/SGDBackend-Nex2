import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import { setDataset } from '../../actions/datasetActions';
import OneDataset from './oneDataset';

const LOAD_DATASET = '/dataset_load';

class LoadDataset extends Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleResetForm = this.handleResetForm.bind(this);
    
    // this.state = {};
  }

  handleChange() {
    let currentDataset = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentDataset[key[0]] = key[1];
    }
    this.props.dispatch(setDataset(currentDataset));
  }

  handleSubmit(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.dataset){
      formData.append(key,this.props.dataset[key]);
    }

    fetchData(LOAD_DATASET, {
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false
    }).then((data) => {
      this.props.dispatch(setMessage(data.success));
    }).catch((err) => {
      this.props.dispatch(setError(err.error));
    });
  }

  handleResetForm() {
    let currentDataset = {
      dataset_id: 0,
      format_name: '',
      display_name: '',
      obj_url: '',
      dbxref_id:'',
      dbxref_type: '',
      date_public: '',
      parent_dataset: '',
      assay_id: '',
      channel_count: '',
      sample_count: '',
      is_in_spell: '',
      is_in_browser: '',
      description: '',
      filenames: '',
      keywords: '',
      pmids: '',
      urls: '',
      lab: '',
      tracks: ''
    };
    this.props.dispatch(setDataset(currentDataset));
  }

  addButton() {
    return (
      <div>
        <div className='row'>
          <div className='columns medium-6'>
            <button type='submit' className="button expanded" >Add Dataset</button>
          </div>
        </div>
      </div>
    );
  }

  addNote() {

    return (
      <div className='row'>
        <div> <h2> Note: </h2> </div>
        <div>NOTE HERE </div>
      </div>
    );
  }
    
  render() {

    return (
      <div>
        <form onSubmit={this.handleSubmit} ref='form'>
          <input name='id' value={this.props.dataset.id} className="hide" />

          <OneDataset dataset={this.props.dataset} onOptionChange={this.handleChange} />

          {this.addButton()}

          {this.addNote()}
	
        </form>

      </div>
    );
  }
}

LoadDataset.propTypes = {
  dispatch: PropTypes.func,
  dataset: PropTypes.object
};


function mapStateToProps(state) {
  return {
    dataset: state.dataset['currentDataset']
  };
}

export default connect(mapStateToProps)(LoadDataset);
