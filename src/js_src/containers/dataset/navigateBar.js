import React, { Component } from 'react';
import PropTypes from 'prop-types';

class NavigateBar extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <div className='row'>
        <div className='columns medium-4 small-4'>
          <button type="button" className="button expanded" onClick={()=>window.open('/dataset/{this.props.dataset}')} disabled={this.props.isDataset}>Update Dataset</button>
        </div>
        <div className='columns medium-4 small-4'>
          <button type="button" className="button expanded" onClick={()=>window.open('/datasetsample/{this.props.dataset}')} disabled={this.props.isSample}>Update Dataset Samples</button>          
        </div>
        <div className='columns medium-4 small-4'>
          <button type="button" className="button expanded" onClick={()=>window.open('/datasettrack/{this.props.dataset}')} disabled={this.props.isTrack}>Update Dataset Tracks</button>
        </div>
      </div>
    );
  }
}

NavigateBar.propTypes = {
  isDataset: PropTypes.bool,
  isSample: PropTypes.bool,
  isTrack: PropTypes.bool,
  dataset: PropTypes.string
};

export default NavigateBar;
