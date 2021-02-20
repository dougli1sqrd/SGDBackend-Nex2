const DEFAULT_STATE = {
  currentSample: {
    datasetsample_id: 0,
    sample_id: 0,
    format_name: '',
    display_name: '',
    obj_url: '',
    dbxref_id:'',
    dbxref_type: '',
    sample_order: '',
    biosample: '',
    strain_name: '',
    description: ''
  }
};

const SET_SAMPLE = 'SET_SAMPLE';

const datasetSampleReducer = (state = DEFAULT_STATE, action) => {
  switch (action.type) {
  case SET_SAMPLE:
    return Object.assign({}, state, action.payload);
  default:
    return state;
  }
};

export default datasetSampleReducer;
