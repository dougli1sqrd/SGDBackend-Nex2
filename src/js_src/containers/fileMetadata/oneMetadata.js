import React, { Component } from 'react';
import PropTypes from 'prop-types';
import TwoColTextField from '../allele/twoColTextField';
import FourColTextField from './fourColTextField';
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

        {/* file year, date, size & extension */}
        <FourColTextField sec_title='Year' name='year' value={this.props.metadata.year} onOpctionChange={this.props.onOptionChange} sec_title2='File date' name2='file_date' value2={this.props.metadata.file_date} sec_title3='File size' name3='file_size' value3={this.props.metadata.file_size} sec_title4='File extension' name4='file_extension' value4={this.props.metadata.file_extension} />

	


	
      </div>

    );
  }
}

OneMetadata.propTypes = {
  metadata: PropTypes.object,
  onOptionChange: PropTypes.func
};

export default OneMetadata;
