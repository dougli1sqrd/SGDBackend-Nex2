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
	
        {/* allele name & references*/}
        <TwoColTextField sec_title='Allele name' name='allele_name' value={this.props.allele.allele_name} onOptionChange={this.props.onOptionChange} sec_title2='Allele name PMIDs (optional)' name2='allele_name_pmids' value={this.props.allele.allele_name_pmids} onOptionChange2={this.props.onOptionChange} />

        {/* affected gene name & references*/}
        <TwoColTextField sec_title='Affected gene name' name='affected_gene' value={this.props.allele.affected_gene} onOptionChange={this.props.onOptionChange} sec_title2='Affected gene name PMIDs (optional)' name2='affected_gene_pmids' value={this.props.allele.affected_gene_pmids} onOptionChange2={this.props.onOptionChange} />
	
        {/* alias names & references*/}



	

        {/* Allele_type */}
        <AutocompleteSection sec_title='Allele_type' id='so_id' value1='display_name' value2='format_name' placeholder='Enter allele_type' selectedIdName='so_id' onOptionChange={this.props.onOptionChange} selectedId={this.allele.so_id} setNewValue={false} />  
	
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
