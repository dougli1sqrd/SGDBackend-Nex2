import React, { Component } from 'react';
import PropTypes from 'prop-types';

import CommentSection from '../phenotype/commentSection';
import TwoColTextField from './twoColTextField';
import OneColTextField from './oneColTextField';
import AutocompleteSection from './autocompleteSection';

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

	ONE ALLELE
	
      </div>

    );
  }
}

OneAllele.propTypes = {
  allele: PropTypes.object,
  onOptionChange: PropTypes.func
};

export default OneAllele;
