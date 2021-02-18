const DEFAULT_STATE = {
  currentTrack: {
    dataset_id: 0,
    track_id: 0,
    format_name: '',
    display_name: '',
    obj_url: '',
    track_order: ''
  }
};

const SET_TRACK = 'SET_TRACK';

const datasetTrackReducer = (state = DEFAULT_STATE, action) => {
  switch (action.type) {
  case SET_TRACK:
    return Object.assign({}, state, action.payload);
  default:
    return state;
  }
};

export default datasetTrackReducer;
