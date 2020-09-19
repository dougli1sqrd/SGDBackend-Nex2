import React, { Component } from 'react';
import CurateLayout from '../curateHome/layout';
// import NewALLELE from './newAllele';
import AlleleBasic from './basic';

class NewAllele extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <CurateLayout>
        <h1>Add Allele</h1>
        <AlleleBasic /> 
      </CurateLayout>
    );
  }

}

export default NewAllele;
