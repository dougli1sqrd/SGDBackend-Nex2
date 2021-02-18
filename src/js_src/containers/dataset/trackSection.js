import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import Loader from '../../components/loader';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import { setTrack } from '../../actions/trackActions';
import { PREVIEW_URL } from '../../constants.js';
import OneDataset from './oneDataset';
const UPDATE_TRACK = '/track_update';
const GET_TRACK = '/get_track_data';

const TIMEOUT = 300000;

class TrackSection extends Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleUpdate = this.handleUpdate.bind(this);
  
    this.state = {
      track_id: null,
      format_name: null,
      preview_url: null,	
      isLoading: false,
      isComplete: false,
    };
  }

  componentDidMount() {
    let url = this.setVariables();
    this.getData(url);
  }

  handleChange() {
    let currentTrack = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentTrack[key[0]] = key[1];
    }
    this.props.dispatch(setTrack(currentTrack));
  }

  handleUpdate(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.track){
      formData.append(key,this.props.track[key]);
    }
    fetchData(UPDATE_TRACK, {
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
            <button type='submit' id='submit' value='0' className="button expanded" onClick={this.handleUpdate.bind(this)} > Update Track data </button>
          </div>
        </div>
      </div>
    );
  }

  getData(url) {
    this.setState({ isLoading: true });
    fetchData(url).then( (data) => {
      let currentTrack = {};
      for (let key in data) {
        currentTrack[key] = data[key];         
      }
      this.props.dispatch(setTrack(currentTrack));
    })
    .catch(err => this.props.dispatch(setError(err.error)))
    .finally(() => this.setState({ isComplete: true, isLoading: false }));
  }

  setVariables() {
    let urlList = window.location.href.split('/');
    let format_name = urlList[urlList.length-1];
    let url = GET_TRACK + '/' + format_name;  
    this.setState({
      format_name: format_name,
      preview_url: `${PREVIEW_URL}` + '/track/' + format_name
    });
    return url;
  }
    
  displayForm() {
    return (
      <div>
        <a href={this.state.preview_url} target='new'>Preview this Track Page</a>
        <form onSubmit={this.handleUpdate} ref='form'>
          <input name='format_name' value={this.props.track.format_name} className="hide" />
          <OneTrack track={this.props.track} onOptionChange={this.handleChange} />
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

TrackSection.propTypes = {
  dispatch: PropTypes.func,
  track: PropTypes.object
};


function mapStateToProps(state) {
  return {
    track: state.track['currentTrack']
  };
}

export default connect(mapStateToProps)(TrackSection);
