import React, { Component } from 'react';
import { connect } from 'react-redux';
// import { push } from 'react-router-redux';
// import { Link } from 'react-router';
import t from 'tcomb-form';

import CategoryLabel from '../../components/categoryLabel';
import CurateLayout from '../curateHome/layout';
import FlexiForm from '../../components/forms/flexiForm';
import { setMessage } from '../../actions/metaActions';
import fetchData from '../../lib/fetchData';
import Loader from '../../components/loader';

const DATA_BASE_URL = '/reservations';

class GeneNameReservationEdit extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: null
    };
  }

  componentDidMount() {
    let url = `${DATA_BASE_URL}/${this.props.params.id}`;
    fetchData(url).then( _data => {
      this.setState({ data: _data });
    });
  }

  handleUpdateSuccess() {
    this.props.dispatch(setMessage('Gene name reservation updated.'));
  }

  handlePmidSuccess() {
    this.props.dispatch(setMessage('Publication associated with gene name reservation.'));
  }

  renderPMIDForm() {
    let data = this.state.data;
    if (!data) return null;
    if (data.reservation_status === 'Unprocessed') return null;
    let pmidSchema = t.struct({
      pmid: t.String
    });
    let pmidOptions = {
      fields: {
        pmid: {
          label: 'PMID'
        }
      }
    };
    let pmidUpdateUrl = `${DATA_BASE_URL}/${this.props.params.id}/pmid`;
    let _defaultData = null;
    if (data.reference.pmid) {
      _defaultData = { pmid: data.reference.pmid };
    }
    return (
      <div>
        <p>Add PMID to change personal communication to reference. The personal communication will only be deleted if it is not used on other gene name reservations.</p>
        <div className='row'>
          <div className='columns small-12 medium-4'>
            <FlexiForm defaultData={_defaultData} onSuccess={this.handlePmidSuccess.bind(this)} requestMethod='POST' tFormSchema={pmidSchema} tFormOptions={pmidOptions} updateUrl={pmidUpdateUrl} submitText='Associate PMID' />
          </div>
        </div>
      </div>
    );
  }

  renderForms() {
    let data = this.state.data;
    let reserveSchema = t.struct({
      display_name: t.String,
      systematic_name: t.maybe(t.String),
      name_description: t.maybe(t.String)
    });
    let reserveOptions = {
      fields: {
        display_name: {
          label: 'Proposed name'
        },
        systematic_name: {
          label: 'Systematic name'
        },
        name_description: {
          type: 'textarea',
          label: 'Name description'
        }
      }
    };
    
    let reserveUpdateUrl = `${DATA_BASE_URL}/${this.props.params.id}`;
    
    if (data) {
      return (
        <div>
          <h3><CategoryLabel category='reserved_name' hideLabel /> Reserved Gene Name: {data.display_name}</h3>
          <div>
            <FlexiForm defaultData={data} onSuccess={this.handleUpdateSuccess.bind(this)} requestMethod='PUT' tFormSchema={reserveSchema} tFormOptions={reserveOptions} updateUrl={reserveUpdateUrl} />
            {this.renderPMIDForm()}
          </div>
        </div>
      );
    }
    return <Loader />;
  }

  render() {
    return (
      <CurateLayout>
        <div className='row'>
          <div className='columns small-12 medium-6'>
            {this.renderForms()}
          </div>
        </div>
      </CurateLayout>
    );
  }
}

GeneNameReservationEdit.propTypes = {
  params: React.PropTypes.object,
  dispatch: React.PropTypes.func
};

function mapStateToProps() {
  return {
  };
}

export default connect(mapStateToProps)(GeneNameReservationEdit);
