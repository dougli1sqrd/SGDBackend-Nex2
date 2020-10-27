import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import { setAllele } from '../../actions/alleleActions';
import OneAllele from './oneAllele';
import AliasRow from './aliasRow';

const ADD_ALLELE = '/allele_add';

class NewAllele extends Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleResetForm = this.handleResetForm.bind(this);
    
    this.state = { alias_count:  1 };
      
  }

  handleChange() {
    let currentAllele = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentAllele[key[0]] = key[1];
    }
    this.props.dispatch(setAllele(currentAllele));
  }

  handleSubmit(e) {
    e.preventDefault();
    let formData = new FormData();
    for(let key in this.props.allele){
      formData.append(key,this.props.allele[key]);
    }

    fetchData(ADD_ALLELE, {
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false
    }).then((data) => {
      this.props.dispatch(setMessage(data.success));
    }).catch((err) => {
      this.props.dispatch(setError(err.error));
    });
  }

  handleResetForm() {
    let currentAllele = {
      id: 0,
      allele_name: '',
      allele_name_pmids: '',
      affected_gene: '',
      affected_gene_pmids: '',
      so_id: '',
      allele_type_pmids: '',
      desc: '',
      desc_pmids: '',
      primary_pmids: '',
      additional_pmids: '',
      review_pmids: ''
    };
    this.props.dispatch(setAllele(currentAllele));
  }

  addButton() {
    return (
      <div>
        <div className='row'>
          <div className='columns medium-6'>
            <button type='submit' className="button expanded" >Add Allele</button>
          </div>
        </div>
      </div>
    );
  }

  handleAddingAliasRow() {
    var count = this.state.alias_count + 1;
    this.setState({ alias_count: count });
  }

  render() {

    var count = this.state.alias_count;
      
    return (
      <div>
        <form onSubmit={this.handleSubmit} ref='form'>
          <input name='id' value={this.props.allele.id} className="hide" />

          <AliasRow set_title='Alias name' name='alias_name' value='' onOptionChange={this.handleChange} />
	
          <OneAllele allele={this.props.allele} onOptionChange={this.handleChange} />

          
          <p><a href='#' onClick={this.handleAddingAliasRow()}>Add Alias</a></p>
/Users/shuai/Downloads/gene_association.sgd.gaf.gz 
          for (var i = 0; i < count; i++) {
            <AliasRow set_title='Alias name' name='alias_name' value='' onOptionChange={this.handleChange} />
          }
	
          {this.addButton()}

        </form>

      </div>
    );
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
