const DEFAULT_STATE = {
  currentAllele: {
    dbentity_id: 0,
    allele_name: '',
    allele_type: '',
    description: ''
  }
};

const SET_ALLELE = 'SET_ALLELE';

const alleleReducer = (state = DEFAULT_STATE, action) => {
  switch (action.type) {
  case SET_ALLELE:
    return Object.assign({}, state, action.payload);
  default:
    return state;
  }
};

export default alleleReducer;
