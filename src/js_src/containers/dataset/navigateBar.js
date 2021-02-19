import React, { Component } from 'react';
import PropTypes from 'prop-types';

class NavigateBar extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {

    let dataset_url = '/dataset/' + this.props.dataset_name;
    let sample_url = '/datasetsample/' + this.props.dataset_name;
    let track_url = '/datasettrack/' + this.props.dataset_name;
    return (
      <div className='row'>
        <div className='columns medium-4 small-4'>
          <button type="button" className="button expanded" onClick={()=>window.open({dataset_url})} disabled={this.props.isDataset}>Update Dataset</button>
        </div>
        <div className='columns medium-4 small-4'>
          <button type="button" className="button expanded" onClick={()=>window.open({sample_url})} disabled={this.props.isSample}>Update Dataset Samples</button>          
        </div>
        <div className='columns medium-4 small-4'>
          <button type="button" className="button expanded" onClick={()=>window.open({track_url})} disabled={this.props.isTrack}>Update Dataset Tracks</button>
        </div>
      </div>
    );
  }
}

NavigateBar.propTypes = {
  isDataset: PropTypes.bool,
  isSample: PropTypes.bool,
  isTrack: PropTypes.bool,
  dataset_name: PropTypes.string
};

export default NavigateBar;
