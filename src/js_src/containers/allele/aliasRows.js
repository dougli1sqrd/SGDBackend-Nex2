import React, { Component } from 'react';
import PropTypes from 'prop-types';

class AliasRows extends Component {
  constructor(props) {
    super(props);
  }
    
  render() {

    let countMap = [0,1,2,3,4];
      
    return (
      <div className='row'>
        <div className='columns medium-6 small-6'>
          <div> <label> Alias name </label> </div>

        {countMap.map(i => {
            return <input type='text' name='alias_name{i}' value={this.props.value} onChange={this.props.onOptionChange} />
        }}}
	    
        </div>
        <div className='columns medium-6 small-6'>
          <div> <label> PMID(s) for alias name (optional) </label> </div>

          {countMap.map(i => {
            return <input type='text' name='alias_pmids' value={this.props.value2} onChange={this.props.onOptionChange} />
          })}
	
        </div>
      </div>
    );
  }
}

AliasRows.propTypes = {
  count: PropTypres.interger,    
  value: PropTypes.string,
  onOptionChange: PropTypes.func,
  sec_title2: PropTypes.string,
  value2: PropTypes.string,
  onOptionChange2: PropTypes.func, 
};

export default AliasRows;
