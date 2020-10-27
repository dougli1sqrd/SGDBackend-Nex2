import React, { Component } from 'react';
import PropTypes from 'prop-types';

class AliasRows extends Component {
  constructor(props) {
    super(props);
  }
    
  render() {

    let countMap = [];
    let alias_pmids = [];
    let alias_name = [];
    for (let i = 0; i < this.props.count; i++) {
      countMap.push(i)
      alias_pmids.push("alias_pmid" + i)
      alias_pmids.push("alias_name" + i)
    }
      
    return (
      <div className='row'>
        <div className='columns medium-6 small-6'>
          <div> <label> Alias name </label> </div>
          {countMap.map(i => {
            return <input type='text' name={this.props.alias_name[i]} value={this.props.value[i]} onChange={this.props.onOptionChange} />;
          })}
        </div>
        <div className='columns medium-6 small-6'>
          <div> <label> PMID(s) for alias name (optional) </label> </div>
          {countMap.map(i => {
            return <input type='text' name={this.props.alias_pmids[i]} value={this.props.value2[i]} onChange={this.props.onOptionChange} />;
          })}
        </div>
      </div>
    );
  }
}

AliasRows.propTypes = {
  count: PropTypes.interger,
  onOptionChange: PropTypes.func,
};

export default AliasRows;
