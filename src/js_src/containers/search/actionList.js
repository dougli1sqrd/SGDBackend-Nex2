import React, { Component } from 'react';
import { Link } from 'react-router';

class ActionList extends Component {
  render() {
    let action_categories = ['locus', 'reference', 'reserved_name', 'download'];
    if(action_categories.includes(this.props.category)){
      if(this.props.category == 'download'){
        /*eslint-disable no-debugger */
        return(
        <Link
          style={{ display: 'inline-block', minWidth: '6rem' }}
          to={{pathname:'file_curate_update', search:`?name=${this.props.displayName.replace(/<[^>]*>?/gm, '')}`}}
        >
          <i className='fa fa-edit' /> Curate
        </Link>);
      }
      else{
        let href = `curate${this.props.href}`;
        return <Link style={{ display: 'inline-block', minWidth: '6rem' }} to={href}><i className='fa fa-edit' /> Curate</Link>;
      }

    }
    return null;
  }
}

ActionList.propTypes = {
  category: React.PropTypes.string,
  href: React.PropTypes.string,
  displayName: React.PropTypes.string
};

export default ActionList;
