import React, { Component } from 'react';
import PropTypes from 'prop-types';
import CurateLayout from '../curateHome/layout';
import { setTrack } from '../../actions/datasetTrackActions';  
import fetchData from '../../lib/fetchData';
import TrackSection from './trackSection';
import { setError, setMessage } from '../../actions/metaActions';

const GET_DATASET = '/get_dataset_data';
const UPDATE_TRACK = '/datasettrack_update';
const DELETE_TRACK = '/datasettrack_delete';

const TIMEOUT = 300000;

class EditTrack extends Component {
  constructor(props) {
    super(props);
    this.state = {
      tracks: []
    };
    this.handleUpdateSubmit = this.handleUpdateSubmit.bind(this);
    this.handleDeleteSubmit = this.handleDeleteSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }

  componentDidMount() {
    let url = this.setVariables();
    this.getData(url);
  }

  getData(url) {
    fetchData(url).then( (data) => {
      this.setState({ tracks: data['tracks'] });
    })
    .catch(err => this.props.dispatch(setError(err.error)));
  }

  setVariables() {
    let urlList = window.location.href.split('/');
    let format_name = urlList[urlList.length-1];
    return GET_DATASET + '/' + format_name;
  }

  handleChange() {
    let currentTrack = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentTrack[key[0]] = key[1];
    }
    this.props.dispatch(setTrack(currentTrack));
  }
    
  handleUpdateSubmit(e) {
    this.updateData(e, UPDATE_TRACK);
  }

  handleDeleteSubmit(e) {
    this.deleteData(e, DELETE_TRACK);
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
    
  trackSections() {
    let sections = this.state.tracks.map((track, i) => {
      return (<TrackSection track={track} index={i} onUpdateSubmit={this.handleUpdateSubmit} onDeleteSubmit={this.handleDeleteSubmit} onOptionChange={this.handleChange} />);
    });
    return sections;
  }
    
  render() {
    return (
      <CurateLayout>
        <h2>Update Dataset Track</h2>
        { this.trackSections() }
      </CurateLayout>
    );
  }

}

EditTrack.propTypes = {
  dispatch: PropTypes.func,
};

export default EditTrack;
