import React, { Component } from 'react';
import { connect } from 'react-redux';
import t from 'tcomb-form';
import PropTypes from 'prop-types';
import FlexiForm from '../../components/forms/flexiForm';
import Loader from '../../components/loader';
import { setMessage, setError } from '../../actions/metaActions';
import { updateData } from './alleleActions';

const DESCRIPTION_LENGTH = 500;
// const ALIAS_WARNING_ID = 'sgdAliasWarning';

class AlleleBasic extends Component {
  handleChange(data) {
    let description = data['description'];
    if (description.length > DESCRIPTION_LENGTH) {
      this.props.dispatch(setError(`Description cannot be greater than ${DESCRIPTION_LENGTH} characters.`));
    }
    // manually hide/show warning for 
    // for (var i = data.aliases.length - 1; i >= 0; i--) {
    //  let d = data.aliases[i];
    //  if (!d) continue;
    //  let pmids = d.pmids;
    // }
  }

  handleSuccess(data) {
    this.props.dispatch(updateData(data));
    this.props.dispatch(setMessage('Allele updated.'));
  }

  render() {
    let data = this.props.data;
    if (!data || this.props.isPending) return <Loader />;  
    let Alias = t.struct({
      alias_id:t.maybe(t.Number),
      alias: t.String,
      pmids: t.maybe(t.String),
      type: t.enums.of([
        'Uniform',
        'Non-uniform',
        'Retired name'
      ], 'Type')
    });
    let bgiSchema = t.struct({
      allele_name : t.maybe(t.String),	  
      allele_name_pmids : t.maybe(t.String),
      affected_gene : t.maybe(t.String),
      affected_gene_pmids : t.maybe(t.String),
      description: t.maybe(t.String),
      description_pmids: t.maybe(t.String),
      aliases: t.list(Alias),
    });
    let aliasLayout = locals => {
      return (
        <div className='row'>
          {this.renderAliasWarning()}
          <div className='columns small-2 hide'>{locals.inputs.alias_id}</div>
          <div className='columns small-4'>{locals.inputs.alias}</div>
          <div className='columns small-3'>{locals.inputs.type}</div>
          <div className='columns small-5'>{locals.inputs.pmids}</div>
          <div className='columns small-2'>{locals.inputs.removeItem}</div>
        </div>
      );
    };
    let bgiOptions = {
      fields: {
        description: {
          type: 'textarea',
          label: 'Description'
        },
        aliases: {
          disableOrder: true,
          item: {
            template: aliasLayout,
            fields: {
              alias_id:{
                label:'ID'
              },
              pmids: {
                label: 'PMIDS'
              }
            }
          }
        }
      }
    };
    let url = `/allele/${this.props.match.params.id}/new_allele`;
    return (
      <div className='row'>
        <div className='columns small-12 medium-6'>
          <FlexiForm defaultData={this.props.data} onChange={this.handleChange.bind(this)} onSuccess={this.handleSuccess.bind(this)} requestMethod='PUT' tFormSchema={bgiSchema} tFormOptions={bgiOptions} updateUrl={url} />
        </div>
      </div>
    );
  }
}

AlleleBasic.propTypes = {
  data: PropTypes.object,
  dispatch: PropTypes.func,
  isPending: PropTypes.bool,
  params: PropTypes.object
};

function mapStateToProps(state) {
  let _data = state.allele.get('data') ? state.allele.get('data').toJS() : null;
  return {
    data: _data,
    isPending: state.allele.get('isPending')
  };
}

export { AlleleBasic as AlleleBasic };
export default connect(mapStateToProps)(AlleleBasic);
