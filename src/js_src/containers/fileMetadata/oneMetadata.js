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

        {/* year & file size */}
        <TwoColTextField sec_title='Year' name='year' value={this.props.metadata.year} onOpctionChange={this.props.onOptionChange} sec_title2='File size' name2='file_size' value2={this.props.metadata.file_size} onOptionChange2={this.props.onOptionChange} />

	


	
      </div>

    );
  }
}

OneMetadata.propTypes = {
  metadata: PropTypes.object,
  onOptionChange: PropTypes.func
};

export default OneMetadata;
