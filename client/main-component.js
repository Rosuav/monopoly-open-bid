import React from 'react';
import {connect} from 'react-redux';
import Property from './property';

class MainComponent extends React.Component {
	render() {
		return <div>
			<h1>Monopoly Open Bidding</h1>
			<p>Place bids on property, yada yada</p>
			<Property name="Mayfair" />
		</div>;
	}
}

export default connect((state, props) => ({
	//Select your state -> props mappings here
	paula: state.paula,
}))(MainComponent);
