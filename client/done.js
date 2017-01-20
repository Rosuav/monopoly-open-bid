import React from 'react';
import {connect} from 'react-redux';
import socksend from './websocket';

class Done extends React.Component {
	toggle_done() {
		socksend("done", {});
	}

	render() {
		return <button className="done" onClick={this.toggle_done.bind(this)}>
			Done (unimpl)
		</button>;
	}
}

export default connect((state, props) => ({
	done: state.done,
	donecount: state.donecount,
}))(Done);
