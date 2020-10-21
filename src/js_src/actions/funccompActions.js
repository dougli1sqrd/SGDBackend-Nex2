const SET_FUNCCOMP = 'SET_FUNCCOMP';
export function setFunccomp(currentFunccomp) {
  return { type: SET_FUNCCOMP, payload: { currentFunccomp: currentFunccomp } };
}