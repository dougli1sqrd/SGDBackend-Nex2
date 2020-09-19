export function updateData (payload) {
  return { type: 'UPDATE_ALLELE_DATA', payload: payload };
}

export function setPending () {
  return { type: 'SET_ALLELE_PENDING' };
}

export function clearPending () {
  return { type: 'CLEAR_ALLELE_PENDING' };
}
