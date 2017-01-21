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
			{` (${this.props.done_count}/${this.props.user_count})`}
		</button>;
	}
}

export default connect((state, props) => ({
	done: state.done,
	done_count: state.done_count || 0,
	user_count: state.users.length,
}))(Done);
