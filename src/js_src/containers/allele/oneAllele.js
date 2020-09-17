import React, { Component } from 'react';
import PropTypes from 'prop-types';

import CommentSection from '../phenotype/commentSection';
//import TwoColTextField from './twoColTextField';
//import OneColTextField from './oneColTextField';
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
        <CommentSection sec_title='desc' name='desc' value={this.props.allele.desc} onOptionChange={this.props.onOptionChange} placeholder='Enter description' rows='3' cols='500' />


	
      </div>

    );
  }
}

OneAllele.propTypes = {
  allele: PropTypes.object,
  onOptionChange: PropTypes.func
};

export default OneAllele;
