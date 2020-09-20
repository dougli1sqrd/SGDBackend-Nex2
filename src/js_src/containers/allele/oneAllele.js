import React, { Component } from 'react';
import PropTypes from 'prop-types';

import CommentSection from '../phenotype/commentSection';
import TwoColTextField from './twoColTextField';
import OneColTextField from './oneColTextField';
import AutocompleteSection from '../phenotype/autocompleteSection';

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
	
        {/* allele name & references */}
        <TwoColTextField sec_title='Allele name' name='allele_name' value={this.props.allele.allele_name} onOptionChange={this.props.onOptionChange} sec_title2='Allele name PMIDs (optional)' name2='allele_name_pmids' value2={this.props.allele.allele_name_pmids} onOptionChange2={this.props.onOptionChange} />

        {/* affected gene name & references */}
        <TwoColTextField sec_title='Affected gene name' name='affected_gene' value={this.props.allele.affected_gene} onOptionChange={this.props.onOptionChange} sec_title2='Affected gene name PMIDs (optional)' name2='affected_gene_pmids' value2={this.props.allele.affected_gene_pmids} onOptionChange2={this.props.onOptionChange} />
	
        {/* alias names & references */}

	

	

	

        {/* Allele type & references */}
        <div className='row'>
          <div className='columns medium-6 small-6'>
            <AutocompleteSection sec_title='Allele type' id='so_id' value1='display_name' value2='' selectedIdName='so_id' placeholder='Enter allele type' onOptionChange={this.props.onOptionChange} selectedId={this.props.allele.so_id} setNewValue={false} /> 
          </div>
          <div className='columns medium-6 small-6'>
            <div> <label> Allele type PMIDs (optional) </label> </div>
            <input type='text' name='allele_type_pmids' value={this.props.allele.allele_type_pmids} onChange={this.props.onOptionChange} />
          </div>
        </div>

	
	
        {/* desctription */}
        <CommentSection sec_title='Description' name='desc' value={this.props.allele.desc} onOptionChange={this.props.onOptionChange} placeholder='Enter description' rows='3' cols='500' />

        {/* literature */}
        <OneColTextField sec_title='Primary Literature (space delimited PMIDs):' name='primary_pmids' value={this.props.allele.primary_pmids} onOptionChange={this.props.onOptionChange} />

        <OneColTextField sec_title='Additional Literature (space delimited PMIDs):' name='additional_pmids' value={this.props.allele.primary_pmids} onOptionChange={this.props.onOptionChange} />

        <OneColTextField sec_title='Review Literature (space delimited PMIDs):' name='review_pmids' value={this.props.allele.primary_pmids} onOptionChange={this.props.onOptionChange} />
	
      </div>

    );
  }
}

OneAllele.propTypes = {
  allele: PropTypes.object,
  onOptionChange: PropTypes.func
};

export default OneAllele;
