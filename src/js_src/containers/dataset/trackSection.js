import React, { Component } from 'react';
import PropTypes from 'prop-types';

class TrackSection extends Component {
  constructor(props) {
    super(props);

    this.handleUpdate = this.handleUpdate.bind(this);
    this.handleDelete = this.handleDelete.bind(this);
      
    this.state = {
      track_id: null,
      format_name: null,
    };
  }

  handleUpdate(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.track){
      formData.append(key,this.props.track[key]);
    }
    this.props.onUpdateSubmit(formData);
  }

  handleDelete(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.track){
      formData.append(key,this.props.track[key]);
    }
    this.props.onDeleteSubmit(formData);
  }

  trackRow() {
    return (
      <div>
        {/* format_name, display_name */}
        <div className='row'>
          <div className='columns medium-6 small-6'>
            <div> <label> format_name </label> </div>
            <input type='text' name='format_name' value={this.props.track.format_name} onChange={this.props.onOptionChange()} />
          </div>
          <div className='columns medium-6 small-6'>
            <div> <label> display_name </label> </div>
            <input type='text' name='display_name' value={this.props.track.display_name} onChange={this.props.onOptionChange()} />
          </div>
        </div>

        {/* obj_url & track_order */}
        <div className='row'>
          <div className='columns medium-10 small-10'>
            <div> <label> dbxref_id </label> </div>
            <input type='text' name='obj_url' value={this.props.track.obj_url} onChange={this.props.onOptionChange()} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> track_order </label> </div>
            <input type='text' name='track_order' value={this.props.track.track_order} onChange={this.props.onOptionChange()} />
          </div>
        </div>

        {/* update & delete button */}
        <div className='row'>	    
          <div className='columns medium-6 small-6'>
            <button type='submit' id='submit' value='0' className="button expanded" onClick={this.handleUpdate.bind(this)} > Update this track </button>
          </div>
          <div className='columns medium-6 small-6'>
            <button type='button' className="button alert expanded" onClick={(e) => { if (confirm('Are you sure you want to delete this track?')) this.handleDelete(e); }} > Delete this track </button>
          </div>
        </div>
      </div>
    );
  }
    
  render() {
    return (
      <div>
        <form onSubmit={this.handleUpdate} ref='form'>
          <input name='datasettrack_id' value={this.props.track.datasettrack_id} className="hide" />
          {this.trackRow()}
          <hr />
        </form>
      </div>
    );
  }
}

TrackSection.propTypes = {
  onUpdateSubmit: PropTypes.func,
  onDeleteSubmit: PropTypes.func,
  onOptionChange: PropTypes.func,
  dispatch: PropTypes.func,
  track: PropTypes.object,
  index: PropTypes.integer
};

export default TrackSection;
