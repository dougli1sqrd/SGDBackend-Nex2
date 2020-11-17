import React, { Component } from 'react';
//import TextField from '../forms/textField';
//import StringField from '../forms/stringField';
//import FormDatePicker from '../../components/formDatePicker';
import Dropzone from 'react-dropzone';
import style from '../style.css';
import LoadingPage from '../../components/loadingPage';
import PropTypes from 'prop-types';
import moment from 'moment'; 
import StringField from '../forms/stringField';

class FileMetadataForm extends Component{
  constructor(props){
    super(props);
        //TODO: add handler functions
    this.state = {
      files: [],
      menus: undefined,
      date: moment().format('YYYY-MM-DD')
    };

    this.handleClear = this.handleClear.bind(this);
    this.renderFileDrop = this.handleDrop.bind(this);
    this.handleDateChange = this.handleDateChange.bind(this);
  }
  handleSubmit(e){
    e.preventDefault();
  }

  handleClear(){
    this.setState({ files: []});
  }

  handleDrop(_files){
    this.setState({files: _files});
  }

  handleDateChange(date){
    this.setState({date: moment(date).format('YYYY-MM-DD')});
  }
  //TODO: modularize this function into component
  renderFileDrop(){
    if(this.state.files.length){
      let file_names = this.state.files.map( (file, index) => {
        return <li key={index}>{file.name}</li>;
      });
      return(<div>
          <ul>{file_names}</ul>
          <a onClick={this.handleClear.bind(this)}>Clear Files</a>
        </div>);
    }
    return (<Dropzone name={'file'} onDrop={this.handleDrop.bind(this)} multiple={true}>
      <p className={style.uploadMsg}>Drop file here or click to select</p>
      <h3 className={style.uploadIcon}><i className='fa fa-cloud-upload'></i></h3>

    </Dropzone>);

  }

  render(){
    if(this.props.fileData == undefined){
      return (<LoadingPage />);
    }

    return (
            <form ref='metaForm' onSubmit={this.handleSubmit.bind(this)} name='fileMetadata'>
                <div>
                    <h1>Add file metadata</h1>
                    <h5>Directions</h5>
                    <ul>
                        <li>Make sure you have file with appropriate fields</li>
                        <li>Acceptable file formats:
                          <span className={'label'}>EXCEL</span>
                        </li>
                    </ul>
                </div>
                <hr />

                <div  className={'row'}>
                  <div className={'columns small-6'}>
                    <StringField id="fname" className={'column small-6'} paramName='displayName' displayName={'Display Name'} placeholder={'Something.xls'} isRequired={true} />
                  </div>
                </div>
            </form>
    );
  }
}

FileMetadataForm.propTypes = {
  fileData: PropTypes.object,
  dispatch: PropTypes.func,
  location: PropTypes.object
};

export default FileMetadataForm;
