import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import { setAllele } from '../../actions/alleleActions';
// import OneAllele from './oneAllele';

const ADD_ALLELE = '/allele_add';

class NewAllele extends Component {
  constructor(props) {
    super(props);

    // this.handleChange = this.handleChange.bind(this);
    // this.handleSubmit = this.handleSubmit.bind(this);
    // this.handleResetForm = this.handleResetForm.bind(this);
  }

  render() {

    return (<div> NEW ALLELE FORM </div>);
  }
}

NewAllele.propTypes = {
  dispatch: PropTypes.func,
  allele: PropTypes.object
};


function mapStateToProps(state) {
  return {
    allele: state.allele['currentAllele']
  };
}

export default connect(mapStateToProps)(NewAllele);
