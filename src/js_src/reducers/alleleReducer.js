/*eslint-disable no-case-declarations */
import { fromJS } from 'immutable';

const DEFAULT_STATE = fromJS({
  data: null,
  isPending: false
});

export default function alleleReducer(state = DEFAULT_STATE, action) {
  switch (action.type) {
  case 'UPDATE_ALLELE_DATA':
    return state.set('data', fromJS(action.payload));
  case 'SET_ALLELE_PENDING':
    return state.set('isPending', fromJS(true));
  case 'CLEAR_ALLELE_PENDING':
    return state.set('isPending', fromJS(false));
  default:
    return state;
  }
}

