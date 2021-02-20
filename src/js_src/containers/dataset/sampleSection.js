import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import { setSample } from '../../actions/datasetSampleActions'; 
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';

const UPDATE_SAMPLE = '/datasetsample_update';
const DELETE_SAMPLE = '/datasetsample_delete';

const TIMEOUT = 300000;

class SampleSection extends Component {
  constructor(props) {
    super(props);

    this.handleUpdate = this.handleUpdate.bind(this);
    this.handleDelete = this.handleDelete.bind(this);
    this.handleChange = this.handleChange.bind(this);    	  
    this.state = {
      sample_id: null,
      format_name: null,
    };
  }

  componentDidMount() {
    this.setData();
  }	
    
  handleUpdate(e) {
    e.preventDefault();
    this.updateData(UPDATE_SAMPLE);
  }

  handleDelete(e) {
    e.preventDefault();
    this.updateData(DELETE_SAMPLE);
  }

  updateData(update_url) {
    let formData = new FormData();
    for(let key in this.props.sample){
      formData.append(key,this.props.sample[key]);
    }  
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
    
  handleChange() {
    let currentSample = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentSample[key[0]] = key[1];
    }
    this.props.dispatch(setSample(currentSample));      
  }

  setData() {
    let currentSample = {};
    let data = this.props.sample;
    for (let key in data) {
      currentSample[key] = data[key];
    }
    this.props.dispatch(setSample(currentSample));  
  }
    
  sampleRow() {
    return (
      <div>
        {/* format_name, display_name */}
        <div className='row'>
          <div className='columns medium-4 small-4'>
            <div> <label> format_name </label> </div>
            <input type='text' name='format_name' value={this.props.sample.format_name} onChange={this.handleChange} />
          </div>
          <div className='columns medium-8 small-8'>
            <div> <label> display_name </label> </div>
            <input type='text' name='display_name' value={this.props.sample.display_name} onChange={this.handleChange} />
          </div>
        </div>

        {/* dbxref_id, dbxref_type,strain_name, biosample, & sample_order */}
        <div className='row'>
          <div className='columns medium-2 small-2'>
            <div> <label> dbxref_id </label> </div>
            <input type='text' name='dbxref_id' id={this.props.index} value={this.props.sample.dbxref_id} onChange={this.handleChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> dbxref_type </label> </div>
            <input type='text' name='dbxref_type' value={this.props.sample.dbxref_type} onChange={this.handleChange} />
          </div>
          <div className='columns medium-3 small-3'>
            <div> <label> strain_name </label> </div>
            <input type='text' name='strain_name' value={this.props.sample.strain_name} onChange={this.handleChange} />
          </div>	    
          <div className='columns medium-3 small-3'>
            <div> <label> biosample </label> </div>
            <input type='text' name='biosample' value={this.props.sample.biosample} onChange={this.handleChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> sample_order </label> </div>
            <input type='text' name='sample_order' value={this.props.sample.sample_order} onChange={this.handleChange} />
          </div>
        </div>

        {/* dbxref_url */}
        <div className='row'>
          <div className='columns medium-12 small-12'>
            <div> <label> dbxref_url </label> </div>
            <input type='text' name='dbxref_url' value={this.props.sample.dbxref_url} onChange={this.handleChange} />
          </div>
        </div>

        {/* description */}
        <div className='row'>
          <div className='columns medium-12 small-12'>
            <div> <label> description </label> </div>
            <input type='text' name='description' value={this.props.sample.description} onChange={this.handleChange} />
          </div>
        </div>

        {/* update & delete button */}
        <div className='row'>	    
          <div className='columns medium-6 small-6'>
            <button type='submit' id='submit' value='0' className="button expanded" onClick={this.handleUpdate.bind(this)} > Update this sample </button>
          </div>
          <div className='columns medium-6 small-6'>
            <button type='button' className="button alert expanded" onClick={(e) => { if (confirm('Are you sure you want to delete this sample?')) this.handleDelete(e); }} > Delete this sample </button>
          </div>
        </div>
      </div>
    );
  }
    
  render() {
    return (
      <div>
        <form onSubmit={this.handleUpdate} ref='form'>
          <input name='datasetsample_id' value={this.props.sample.datasetsample_id} className="hide" />
          {this.sampleRow()}
          <hr />
        </form>
      </div>
    );
  }
}

SampleSection.propTypes = {
  dispatch: PropTypes.func,
  sample: PropTypes.object,
  index: PropTypes.integer
};

function mapStateToProps(state) {
  return {
    sample: state.sample['currentSample']
  };
}

export default connect(mapStateToProps)(SampleSection);

