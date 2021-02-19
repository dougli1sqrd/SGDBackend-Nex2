import React, { Component } from 'react';
import CurateLayout from '../curateHome/layout';
import fetchData from '../../lib/fetchData';
// import SampleSection from './sampleSection';
import { setError } from '../../actions/metaActions';

const GET_DATASET = '/get_dataset_data';

class EditSample extends Component {
  constructor(props) {
    super(props);
    this.state = {
      samples: []
    };
  }

  componentDidMount() {
    let url = this.setVariables();
    console.log('url='+url);
    this.getData(url);
  }

  getData(url) {
    fetchData(url).then( (data) => {
      console.log('samples='+data['samples']);
      console.log('dataset='+data);
      this.setState({ samples: data['samples'] });
    })
    .catch(err => this.props.dispatch(setError(err.error)));
  }

  setVariables() {
    let urlList = window.location.href.split('/');
    let format_name = urlList[urlList.length-1];
    return GET_DATASET + '/' + format_name;
  }

  sampleSections() {
    let sections = this.state.samples.map((sample, i) => {
      // return (<SampleSection sample={sample} index={i} />);
      return (<div>{i} : {sample.format_name}</div>);
    });
    return sections;
  }
    
  render() {
    return (
      <CurateLayout>
        <h2>Update Dataset Samples</h2>
        { this.sampleSections }
      </CurateLayout>
    );
  }

}

export default EditSample;
