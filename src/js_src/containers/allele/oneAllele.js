import React, { Component } from 'react';
import PropTypes from 'prop-types';

import CommentSection from '../phenotype/commentSection';
//import TwoColTextField from './twoColTextField';
import OneColTextField from './oneColTextField';
//import AutocompleteSection from './autocompleteSection';

class OneAllele extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: this.props.allele
    };
  }

  render() {
	
    return (

      <div>


	
        {/* desctription */}
        <CommentSection sec_title='Description' name='desc' value={this.props.allele.desc} onOptionChange={this.props.onOptionChange} placeholder='Enter description' rows='3' cols='500' />

        {/* literature */}
        <OneColTextField sec_title='Primary (space delimited PMIDs):' name='primary_pmids' value={this.props.allele.primary_pmids} onOptionChange={this.props.onOptionChange} />

        <OneColTextField sec_title='Additional (space delimited PMIDs):' name='additional_pmids' value={this.props.allele.primary_pmids} onOptionChange={this.props.onOptionChange} />

        <OneColTextField sec_title='Review (space delimited PMIDs):' name='review_pmids' value={this.props.allele.primary_pmids} onOptionChange={this.props.onOptionChange} />
	
      </div>

    );
  }
}

OneAllele.propTypes = {
  allele: PropTypes.object,
  onOptionChange: PropTypes.func
};

export default OneAllele;
