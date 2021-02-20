import React, { Component } from 'react';
import PropTypes from 'prop-types';

class SampleSection extends Component {
  constructor(props) {
    super(props);

    this.handleUpdate = this.handleUpdate.bind(this);
    this.handleDelete = this.handleDelete.bind(this);
      
    this.state = {
      sample_id: null,
      format_name: null,
    };
  }

  handleUpdate(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.sample){
      formData.append(key,this.props.sample[key]);
    }
    this.props.onUpdateSubmit(formData);
  }

  handleDelete(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.sample){
      formData.append(key,this.props.sample[key]);
    }
    this.props.onDeleteSubmit(formData);
  }

  sampleRow() {
    return (
      <div>
        {/* format_name, display_name */}
        <div className='row'>
          <div className='columns medium-4 small-4'>
            <div> <label> format_name </label> </div>
            <input type='text' name='format_name' value={this.props.sample.format_name} onChange={this.onOptionChange()} />
          </div>
          <div className='columns medium-8 small-8'>
            <div> <label> display_name </label> </div>
            <input type='text' name='display_name' value={this.props.sample.display_name} onChange={this.onOptionChange()} />
          </div>
        </div>

        {/* dbxref_id, dbxref_type,strain_name, biosample, & sample_order */}
        <div className='row'>
          <div className='columns medium-2 small-2'>
            <div> <label> dbxref_id </label> </div>
            <input type='text' name='dbxref_id' value={this.props.sample.dbxref_id} onChange={this.onOptionChange()} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> dbxref_type </label> </div>
            <input type='text' name='dbxref_type' value={this.props.sample.dbxref_type} onChange={this.props.onOptionChange()} />
          </div>
          <div className='columns medium-3 small-3'>
            <div> <label> strain_name </label> </div>
            <input type='text' name='strain_name' value={this.props.sample.strain_name} onChange={this.props.onOptionChange()} />
          </div>	    
          <div className='columns medium-3 small-3'>
            <div> <label> biosample </label> </div>
            <input type='text' name='biosample' value={this.props.sample.biosample} onChange={this.props.onOptionChange()} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> sample_order </label> </div>
            <input type='text' name='sample_order' value={this.props.sample.sample_order} onChange={this.props.onOptionChange()} />
          </div>
        </div>

        {/* dbxref_url */}
        <div className='row'>
          <div className='columns medium-12 small-12'>
            <div> <label> dbxref_url </label> </div>
            <input type='text' name='dbxref_url' value={this.props.sample.dbxref_url} onChange={this.props.onOptionChange()} />
          </div>
        </div>

        {/* description */}
        <div className='row'>
          <div className='columns medium-12 small-12'>
            <div> <label> description </label> </div>
            <input type='text' name='description' value={this.props.sample.description} onChange={this.props.onOptionChange()} />
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
          <input name='format_name' value={this.props.sample.format_name} className="hide" />
          {this.sampleRow()}
          <hr />
        </form>
      </div>
    );
  }
}

SampleSection.propTypes = {
  onUpdateSubmit: PropTypes.func,
  onDeleteSubmit: PropTypes.func,
  onOptionChange: PropTypes.func,
  dispatch: PropTypes.func,
  sample: PropTypes.object,
  index: PropTypes.integer
};

export default SampleSection;
