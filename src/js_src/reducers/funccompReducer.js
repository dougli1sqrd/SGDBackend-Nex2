const DEFAULT_STATE = {
    currentFunccomp: {
        annotation_id: 0,
        dbentity_id: '',
        taxonomy_id: '',
        reference_id: '',
        source_id: '',
        eco_id: '',
        ro_id: '',
        dbxref_id: '',
        obj_url: '',
        direction: '',
        comments: ''
    }
};

const SET_FUNCCOMP = 'SET_FUNCCOMP';

const funccompReducer = (state = DEFAULT_STATE, action) => {
    switch (action.type) {
        case SET_FUNCCOMP:
            return Object.assign({}, state, action.payload);
        default:
            return state;
    }
};

export default funccompReducer;