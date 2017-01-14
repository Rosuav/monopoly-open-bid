import React from 'react';
import {connect} from 'react-redux';
import Property from './property';
import Login from './login';

class MainComponent extends React.Component {
	render() {
		return <div>
			<h1>Monopoly Open Bidding</h1>
			<p>Place bids on property, yada yada</p>
			<ul className="userlist">{this.props.users.map((u,i) => <li key={i}>{u[0] + ": " + u[1]}</li>)}</ul>
			{this.props.user ? this.props.order.map((p,i) => <Property key={i} name={p} {...this.props.properties[p]}/>) : <Login/>}
		</div>;
	}
}

export default connect((state, props) => ({
	//Select your state -> props mappings here
	user: state.user,
	properties: state.properties,
	order: state.order,
	users: state.users,
}))(MainComponent);
