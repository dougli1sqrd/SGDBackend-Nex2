import React, { Component } from 'react';
import PropTypes from 'prop-types';
import TwoColTextField from '../allele/twoColTextField';

// import AutocompleteSection from '../phenotype/autocompleteSection';

class OneMetadata extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: this.props.allele
    };
  }

  render() {
	
    return (

      <div>

        {this.props.metadata.sgdid}
	
        {this.props.metadata.s3_url}
	
        {/* file display name & previous file name*/}
        <TwoColTextField sec_title='File display name' name='display_name' value={this.props.metadata.display_name} onOptionChange={this.props.onOptionChange} sec_title2='Previous file name' name2='previous_file_name' value2={this.props.metadata.previous_file_name} onOptionChange2={this.props.onOptionChange} />

        {/* file year, date, size, extension & file status */}
        <div className='row'>
          <div className='columns medium-2 small-2'>
            <div> <label> Year </label> </div>
            <input type='text' name='year' value={this.props.metadata.year} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> File date </label> </div>
            <input type='text' name='file_date' value={this.props.metadata.file_date} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> File size </label> </div>
            <input type='text' name='file_size' value={this.props.metadata.file_size} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> File extension </label> </div>
            <input type='text' name='file_extension' value={this.props.metadata.file_extension} onChange={this.props.onOptionChange} />
          </div>
          <div className='columns medium-2 small-2'>
            <div> <label> File status </label> </div>
            <input type='text' name='dbentity_status' value={this.props.metadata.dbentity_status} onChange={this.props.onOptionChange} />
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
