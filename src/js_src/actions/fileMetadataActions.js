const SET_FILE_METADATA = 'SET_FILE_METADATA';
export function setFileMetadata(currentFileMetadata) {
  return { type: SET_FILE_METADATA, payload: { currentFileMetadata: currentFileMetadata } };
}
