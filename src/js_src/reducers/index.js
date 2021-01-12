import authReducer from './authReducer';
import metaReducer from './metaReducer';
import litReducer from './litReducer';
import locusReducer from './locusReducer';
import searchReducer from './searchReducer';
import ptmReducer from './ptmReducer';
import newsLetterReducer from './newsLetterReducer';
import regulationReducer from './regulationReducer';
import diseaseReducer from './diseaseReducer';
import phenotypeReducer from './phenotypeReducer';
import alleleReducer from './alleleReducer';
import authorResponseReducer from './authorResponseReducer';
import litGuideReducer from './litGuideReducer';
import fileMetadataReducer from './fileMetadataReducer';

export default {
  auth: authReducer,
  meta: metaReducer,
  lit: litReducer,
  locus: locusReducer,
  search: searchReducer,
  ptm:ptmReducer,
  newsLetter:newsLetterReducer,
  regulation:regulationReducer,
  disease: diseaseReducer,
  phenotype:phenotypeReducer,
  allele:alleleReducer,
  authorResponse:authorResponseReducer,
  litguide:litGuideReducer,
  metadata: fileMetadataReducer
};
