const SET_SUPPL_FILE = 'SET_SUPPL_FILE';
export function setSupplFile(currentSupplFile) {
  return { type: SET_SUPPL_FILE, payload: { currentSupplFile: currentSupplFile } };
}
