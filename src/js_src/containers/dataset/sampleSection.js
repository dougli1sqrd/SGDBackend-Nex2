import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import Loader from '../../components/loader';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import { setSample } from '../../actions/datasetSampleActions';
const UPDATE_SAMPLE = '/sample_update';
const GET_SAMPLE = '/get_dataset_data';

const TIMEOUT = 300000;

class SampleSection extends Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleUpdate = this.handleUpdate.bind(this);
  
    this.state = {
      sample_id: null,
      format_name: null,
      isLoading: false,
      isComplete: false,
    };
  }

  componentDidMount() {
    let url = this.setVariables();
    this.getData(url);
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
            <button type='submit' id='submit' value='0' className="button expanded" onClick={this.handleUpdate.bind(this)} > Update Sample data </button>
          </div>
        </div>
      </div>
    );
  }

  getData(url) {
    this.setState({ isLoading: true });
    fetchData(url).then( (data) => {
      let currentSample = {};
      for (let key in data) {
        currentSample[key] = data[key];         
      }
      this.props.dispatch(setSample(currentSample));
    })
    .catch(err => this.props.dispatch(setError(err.error)))
    .finally(() => this.setState({ isComplete: true, isLoading: false }));
  }

  setVariables() {
    let urlList = window.location.href.split('/');
    let format_name = urlList[urlList.length-1];
    let url = GET_SAMPLE + '/' + format_name;  
    this.setState({
      format_name: format_name,
    });
    return url;
  }
    
  displayForm() {
    return (
      <div>
        <form onSubmit={this.handleUpdate} ref='form'>
          <input name='format_name' value={this.props.sample.format_name} className="hide" />
          {this.props.sample.format_name}
          HELLO WORLD
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
