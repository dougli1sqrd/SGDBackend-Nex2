import React, { Component } from 'react';
import PropTypes from 'prop-types';

class AliasRow extends Component {
  constructor(props) {
    super(props);
    this.state = {
      // just to have this section in case we need to do something here
      sec_title: props.sec_title
    };
  }

  render() {
    return (
      <div className='row'>
        <div className='columns medium-4 small-4'>
          <label> { this.state.sec_title } </label> 
        </div>
        <div className='columns medium-8 small-8'>
          <input type='text' name={this.props.name} value={this.props.value} onChange={this.props.onOptionChange} />
        </div>
      </div>
    );
  }
}

AliasRow.propTypes = {
  sec_title: PropTypes.string,
  name: PropTypes.string,
  value: PropTypes.string,
  onOptionChange: PropTypes.func
};

export default AliasRow;
