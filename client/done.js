import React from 'react';
import {connect} from 'react-redux';
import socksend from './websocket';

class Done extends React.Component {
	toggle_done() {
		socksend("done", {});
	}

	render() {
		return <button className="done" onClick={this.toggle_done.bind(this)}>
			{this.props.done ? "Not done yet" : "I'm done!"}
			{` (${this.props.done_count||0}/${this.props.user_count})`}
		</button>;
	}
}

export default connect(
	({done, done_count, user_count}) => ({done, done_count, user_count})
)(Done);
