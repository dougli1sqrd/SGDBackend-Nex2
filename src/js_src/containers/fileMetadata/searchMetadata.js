import React, { Component } from 'react';
import PropTypes from 'prop-types';
import fetchData from '../../lib/fetchData';
import Loader from '../../components/loader';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { setError, setMessage } from '../../actions/metaActions';
import { setFileMetadta} from '../../actions/fileMetadataActions';
// import TextFieldSection from './textFieldSection';
const GET_FILE_METADATA = '/get_file_metadata/';

const TIMEOUT = 240000;

class SearchMetadata extends Component {

  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
    this.handleGetMetadata = this.handleGetMetadata.bind(this);
    
    this.state = {
      isComplete: false,
      metadata: [],
      isLoading: false
    };    
  }

  handleChange() {
    let currentMetadata = {};
    let data = new FormData(this.refs.form);
    for (let key of data.entries()) {
      currentMetadata[key[0]] = key[1];
    }
    this.props.dispatch(setFileMetadata(currentMetadata));
  }

  handleGetMetadata(){
    let url = this.setGetUrl();
    this.setState({ metadata: [], isLoading: true });
    fetchData(url, { timeout: TIMEOUT }).then( (data) => {
      this.setState({ metadata: data });
    })
    .catch(err => this.props.dispatch(setError(err.error)))
    .finally(() => this.setState({ isLoading: false, isComplete: true }));
  }

  setGetUrl() {
    let query = this.props.metadata['display_name'];
    let url = GET_FILE_METADATA + query;
    if (query == '') {
      this.props.dispatch(setMessage('Please enter the file name.'));
    }
    return url;
  }

  addSubmitButton(name) {
    return (
      <div>
        <div className='row'>
          <div className='columns medium-6'>
            <button type='submit' className="button expanded" > {name} </button>
          </div>
        </div>
      </div>
    );
  }

  getCurateLink(sgdid) {
    return (
      <form method='POST' action='/#/edit_file_metadata' target='new'>
        <input type='hidden' name='sgdid' value={sgdid} />
        <input type="submit" value='Curate' />
      </form>
    );
  }

  // WORK FROM HERE
    
  getDataRows(data) {

    window.localStorage.clear();

    let rows = data.map((d, i) => {
      let identifier_list = d.annotation_identifier_list;
      let genes = [];
      let annotation_id = 0;
      for (let j = 0; j < identifier_list.length; j++) {
        let identifiers = identifier_list[j].split('|');
        genes.push(identifiers[0]);
        if (annotation_id == 0) {
          annotation_id = identifiers[1];
        }
      }
      let gene_list = genes.join(' ');
      let gene_identifier_list = identifier_list.join(' ');
      let details = this.format_details(d.details);
      let min = 1;
      let max = 1000;
      let id =  min + (Math.random() * (max-min));
      let genesID = 'genes_' + id;
      let annotID = 'annotation_id_' + id;
      let groupID = 'group_id_' + id;
      window.localStorage.setItem(genesID, gene_identifier_list);
      window.localStorage.setItem(annotID, annotation_id);
      window.localStorage.setItem(groupID, d.group_id);
      return (
        <tr key={i}>
          <td>{ gene_list }</td>
          <td>{ d.phenotype}</td>
          <td>{ d.experiment_type }</td>
          <td>{ d.mutant_type}</td>
          <td>{ d.strain_background }</td>
          <td>{ details }</td>
          <td>{ d.paper }</td>
          <td><Link to={`/edit_phenotype/${id}`} target='new'><i className='fa fa-edit' /> Curate </Link></td> 
        </tr>
      );
    });
    return rows;
  }


  displayMetadata() {
    let data = this.state.metadata;
    if (data.length > 0) {
      let rows = this.getDataRows(data);
      return (
        <div>	    
          { this.searchForm() }
          <table>
            <thead>
              <tr>
                <th>Gene(s)</th> 
                <th>FileMetadata</th>
                <th>Experiment Type</th>
                <th>Mutant Type</th>
                <th>Strain Background</th>
                <th>Chemicals/Details</th>
                <th>Reference</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              { rows }
            </tbody>
          </table>
        </div>
      );
    }
    else {
      return (
        <div>
          <div>{ this.searchForm() }</div>
          <div> No File found for your input(s).</div>
        </div>
      );
    }
  }

  searchForm() {
    return (
      <div>
        <form onSubmit={this.handleGetMetadata} ref='form'>
          <h4>Search metadata by gene name(s) and/or reference:</h4>
          <TextFieldSection sec_title='Gene(s) (SGDID, Systematic Name, eg. YFL039C, S000002429) ("|" delimited)' name='genes' value={this.props.phenotype.genes} onOptionChange={this.handleChange} />
          <TextFieldSection sec_title='Reference (SGDID, PMID, Reference_id, eg. SGD:S000185012, 27650253, reference_id:307729)' name='reference' value={this.props.phenotype.reference} onOptionChange={this.handleChange} />
          {this.addSubmitButton('Search')}    
        </form>
      </div>
    );
  }

  render() {
    if (this.state.isLoading) {
      return (
	<div>
          <div>Please wait while we are retrieving the file metadata from the database.</div>
          <div><Loader /></div>
        </div>
      );
    }
    if (this.state.isComplete) {
      return this.displayMetadata();
    }
    else {
      return this.searchForm();
    }
  }
}

SearchFileMetadata.propTypes = {
  dispatch: PropTypes.func,
  metadata: PropTypes.object
};


function mapStateToProps(state) {
  return {
    metadata: state.metadata['currentFileMetadata']
  };
}

export default connect(mapStateToProps)(SearchMetadata);
