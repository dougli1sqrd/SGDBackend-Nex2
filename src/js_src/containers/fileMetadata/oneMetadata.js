import React, { Component } from 'react';
import PropTypes from 'prop-types';
// import TwoColTextField from '../allele/twoColTextField';

// import AutocompleteSection from '../phenotype/autocompleteSection';

class OneMetadata extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: this.props.metadata
    };
  }

  render() {
	
    return (

      <div>
        <div>SGDID: {this.props.metadata.sgdid} <a href='{this.props.metadata.s3_url}' target='new'>s3_url</a></div>
	
        {/* file display name & previous file name & description */}
        <div className='row'>
          <div className='columns medium-4 small-4'>
            <div> <label> display_name </label> </div>
            <input type='text' name='display_name' value={this.props.metadata.display_name} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-4 small-4'>
            <div> <label> previous_file_name </label> </div>
            <input type='text' name='previous_file_name' value={this.props.metadata.previous_file_name} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-4 small-4'>
            <div> <label> description </label> </div>
            <input type='text' name='description' value={this.props.metadata.description} onChange={this.props.onOptionChange} />
          </div>
        </div>

	
        {/* file year, date, size, extension & file status */}
        <div className='row'>
          <div className='columns medium-1 small-1'>
            <div> <label> year </label> </div>
            <input type='text' name='year' value={this.props.metadata.year} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> file_date </label> </div>
            <input type='text' name='file_date' value={this.props.metadata.file_date} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> file_size </label> </div>
            <input type='text' name='file_size' value={this.props.metadata.file_size} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> file_extension </label> </div>
            <input type='text' name='file_extension' value={this.props.metadata.file_extension} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> file_status </label> </div>
            <input type='text' name='dbentity_status' value={this.props.metadata.dbentity_status} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-3 small-3'>
            <div> <label> keyword(s) ('|' delimited)</label> </div>
            <input type='text' name='keywords' value={this.props.metadata.keywords} onChange={this.props.onOptionChange} />
          </div>
	


        </div>


	
      </div>

    );
  }
}

OneMetadata.propTypes = {
  metadata: PropTypes.object,
  onOptionChange: PropTypes.func
};

export default OneMetadata;
