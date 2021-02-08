const DEFAULT_STATE = {
  currentSupplFile: {
    files: []
  }
};

const SET_SUPPL_FILE = 'SET_SUPPL_FILE';

const supplFileReducer = (state = DEFAULT_STATE, action) => {
  switch (action.type) {
  case SET_SUPPL_FILE:
    return Object.assign({}, state, action.payload);
  default:
    return state;
  }
};

export default supplFileReducer;
