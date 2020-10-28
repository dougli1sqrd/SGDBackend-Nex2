import React, { Component } from 'react';
import PropTypes from 'prop-types';

class AliasRows extends Component {
  constructor(props) {
    super(props);
  }
    
  render() {
      
    return (
      <div className='row'>
        <div className='columns medium-6 small-6'>
          <div> <label> Alias name(s) </label> </div>
          <input type='text' name='alias_name_1' value='' onChange={this.props.onOptionChange} />
          <input type='text' name='alias_name_2' value='' onChange={this.props.onOptionChange} />
        </div>
        <div className='columns medium-6 small-6'>
          <div> <label> PMID(s) for alias name (optional) </label> </div>
          <input type='text' name='alias_pmids-1' value='' onChange={this.props.onOptionChange} />
          <input type='text' name='alias_pmids-2' value='' onChange={this.props.onOptionChange} />
        </div>
      </div>
      <div className='row'>
        <div>(use | to separate multiple alias names or pmid sets for multiple aliases)</div>
      </div>
      <div className='row'>
        <div><hr></hr></div>
      </div>
    );
  }
}

AliasRows.propTypes = {
  onOptionChange: PropTypes.func,
};

export default AliasRows;
