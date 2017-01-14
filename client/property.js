import React from 'react';
import {connect} from 'react-redux';
import * as actions from './actions';

export default connect()(class Property extends React.Component {
	update(e) {
		e.preventDefault();
		console.log("Stub - new bid is", this.refs.bid.value);
		//this.props.dispatch(actions.fetch_hello());
	}

	render() {
		return <form onSubmit={this.update.bind(this)}>
			<h3>{this.props.name}</h3>
			<input type="number" ref="bid" />
			<input type="submit" value="Bid" />
		</form>;
	}
})
