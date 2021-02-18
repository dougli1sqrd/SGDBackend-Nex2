import React, { Component } from 'react';
import CurateLayout from '../curateHome/layout';
import TrackSection from './trackSection';

class EditTrack extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <CurateLayout>
        <h1>Update Dataset Samples</h1>
        <TrackSection /> 
      </CurateLayout>
    );
  }

}

export default EditTrack;
