import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import Loader from '../../components/loader';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import { setSample } from '../../actions/datasetSampleActions';
const UPDATE_SAMPLE = '/datasetsample_update';

const TIMEOUT = 300000;

class SampleSection extends Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleUpdate = this.handleUpdate.bind(this);
  
    this.state = {
      sample_id: null,
      format_name: null,
    };
  }

  handleChange() {
    let currentSample = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentSample[key[0]] = key[1];
    }
    this.props.dispatch(setSample(currentSample));
  }

  handleUpdate(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.sample){
      formData.append(key,this.props.sample[key]);
    }
    fetchData(UPDATE_SAMPLE, {
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
            <button type='submit' id='submit' value='0' className="button expanded" onClick={this.handleUpdate.bind(this)} > Update </button>
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
          {this.props.sample.format_name}
          {this.addButtons()}          	
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

export default SampleSection;

//function mapStateToProps(state) {
//  return {
//    sample: state.sample['currentSample']
//  };
// }

// export default connect(mapStateToProps)(SampleSection);
