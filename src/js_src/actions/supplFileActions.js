const SET_SUPPL_FILE = 'SET_SUPPL_FILE';
export function setSupplFile(currentAllele) {
  return { type: SET_SUPPL_FILE, payload: { currentSupplFile: currentSupplFile } };
}
