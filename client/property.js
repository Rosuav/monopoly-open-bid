import React from 'react';
import {connect} from 'react-redux';
import * as actions from './actions';
import socksend from './websocket';

export default connect()(class Property extends React.Component {
	update(e) {
		e.preventDefault();
		socksend("bid", {name: this.props.name, value: this.refs.bid.value});
	}

	render() {
		return <form onSubmit={this.update.bind(this)}>
			<h3 style={{backgroundColor: this.props.color, color: this.props.fg || "black"}}>{this.props.name}</h3>
			<p>
				Current high bid:<br />(nobody) {this.props.facevalue}
			</p>
			<div>
				<input type="number" ref="bid" />
				<input type="submit" value="Bid" />
			</div>
		</form>;
	}
})
