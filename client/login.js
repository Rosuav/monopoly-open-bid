import React from 'react';
import {connect} from 'react-redux';
import socksend from './websocket';

export default connect()(class Login extends React.Component {
	submit(e) {
		e.preventDefault();
		socksend("login", {room: this.refs.room.value, name: this.refs.name.value});
	}

	render() {
		return <form onSubmit={this.submit.bind(this)}>
			<h3>Log in</h3>
			<label>Room: <input ref="room" /></label><br/>
			<label>Name: <input ref="name" /></label><br/>
			<input type="submit" value="Register/log in" />
		</form>;
	}
})
