import React, { Component } from 'react';
import CurateLayout from '../curateHome/layout';
import SampleSection from './sampleSection';

class EditSample extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <CurateLayout>
        <h1>Update Dataset Samples</h1>
        <SampleSection /> 
      </CurateLayout>
    );
  }

}

export default EditSample;
