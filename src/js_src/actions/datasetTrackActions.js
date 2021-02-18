const SET_TRACK = 'SET_TRACK';
export function setTrack(currentTrack) {
  return { type: SET_TRACK, payload: { currentTrack: currentTrack } };
}
