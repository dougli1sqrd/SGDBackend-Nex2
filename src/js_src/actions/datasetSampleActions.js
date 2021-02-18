const SET_SAMPLE = 'SET_SAMPLE';
export function setSample(currentSample) {
  return { type: SET_SAMPLE, payload: { currentSample: currentSample } };
}
