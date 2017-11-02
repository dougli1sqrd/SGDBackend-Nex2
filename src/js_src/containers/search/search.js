import React, { Component } from 'react';
import { createMemoryHistory } from 'react-router';
import { connect } from 'react-redux';
import _ from 'underscore';

import style from './style.css';
import fetchData from '../../lib/fetchData';
import FilterSelector from './filterSelector/filterSelector';
import SearchBreadcrumbs from './searchBreadcrumbs';
import SearchControls from './searchControls';
import ResultsList from './resultsList';
import ResultsTable from './resultsTable';
import { SMALL_COL_CLASS, LARGE_COL_CLASS, SEARCH_API_ERROR_MESSAGE } from '../../constants';
import { receiveResponse, setError, setPending } from './searchActions';
import Loader from '../../components/loader';
import LoadingPage from '../../components/loadingPage';

// used to test rendering fixture response
import fixtureResponse from './tests/fixtureResponse';

import {
  selectActiveCategory,
  selectErrorMessage,
  selectIsError,
  selectIsPending,
  selectIsReady,
  selectQueryParams,
  selectResults,
  selectPageSize
} from '../../selectors/searchSelectors';

const BASE_SEARCH_URL = '/get_search_results';

class SearchComponent extends Component {
  // fetch data at start
  componentDidMount() {
    // this.fetchFixtureData(); // uncomment to use fixture mode
    this.fetchSearchData();
  }

  // fetch data whenever URL changes within /search
  componentDidUpdate (prevProps) {
    if (prevProps.queryParams !== this.props.queryParams) {
      this.fetchSearchData();
    }
  }

  fetchFixtureData() {
    this.props.dispatch(receiveResponse(fixtureResponse, this.props.queryParams));
    this.props.dispatch(setError(false));
    this.props.dispatch(setPending(false));
  }

  fetchSearchData() {
    // edit for pagination
    let size = this.props.pageSize;
    let _limit = size;
    let _offset = (this.props.currentPage - 1) * size;
    let qp = _.clone(this.props.queryParams);
    qp.limit = _limit;
    qp.offset = _offset;
    let tempHistory = createMemoryHistory('/');
    let searchUrl = tempHistory.createPath({ pathname: BASE_SEARCH_URL, query: qp });
    this.props.dispatch(setPending(true));
    fetchData(searchUrl)
      .then( (data) => {
        this.props.dispatch(receiveResponse(data, this.props.queryParams));
        this.props.dispatch(setError(false));
        this.props.dispatch(setPending(false));
      })
      .catch( (e) => {
        this.props.dispatch(setPending(false));
        if (process.env.NODE_ENV === 'production') {
          this.props.dispatch(setError(SEARCH_API_ERROR_MESSAGE));
        } else {
          throw(e);
        }
      });
  }

  renderResultsNode() {
    if (this.props.isPending) {
      return <div style={{ minHeight: '40rem' }}><Loader /></div>;
    }
    if (this.props.isList) {
      return <ResultsList entries={this.props.results} />;
    } else {
      return <ResultsTable entries={this.props.results} />;      
    }
  }

  renderErrorNode() {
    if (!this.props.isError) {
      return null;
    }
    return (
      <div className='alert alert-warning'>
        <h3>Oops, Error</h3>
        <p>{this.props.errorMessage}</p>
      </div>
    );
  }

  render() {
    if (!this.props.isReady) return <LoadingPage />;
    return (
      <div className={style.root}>
        {this.renderErrorNode()}
        <div className='row'>
          <div className={SMALL_COL_CLASS}>
            <FilterSelector />
          </div>
          <div className={LARGE_COL_CLASS}>
            <SearchBreadcrumbs />
            <SearchControls />
            {this.renderResultsNode()}
            <SearchControls />
          </div>
        </div>
      </div>
    );
  }
}

SearchComponent.propTypes = {
  activeCategory: React.PropTypes.string,
  currentPage: React.PropTypes.number,
  dispatch: React.PropTypes.func,
  errorMessage: React.PropTypes.string,
  history: React.PropTypes.object,
  isError: React.PropTypes.bool,
  isPending: React.PropTypes.bool,
  isReady: React.PropTypes.bool,
  isList: React.PropTypes.bool,
  pageSize: React.PropTypes.number,
  queryParams: React.PropTypes.object,
  results: React.PropTypes.array
};

function mapStateToProps(state) {
  let _queryParams = selectQueryParams(state);
  let _isList = (_queryParams.mode === 'list');
  let _currentPage = parseInt(_queryParams.page) || 1;
  let _activeCategory = selectActiveCategory(state);
  return {
    activeCategory: _activeCategory,
    currentPage: _currentPage,
    errorMessage: selectErrorMessage(state),
    isError: selectIsError(state),
    isPending: selectIsPending(state),
    isReady: selectIsReady(state),
    isList: _isList,
    pageSize: selectPageSize(state),
    queryParams: _queryParams,
    results: selectResults(state)
  };
}

export { SearchComponent as SearchComponent };
export default connect(mapStateToProps)(SearchComponent);
