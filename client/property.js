import React from 'react';
import {connect} from 'react-redux';
import socksend from './websocket';

export default connect()(class Property extends React.Component {
	submit(e) {
		e.preventDefault();
		socksend("bid", {name: this.props.name, value: this.refs.bid.value});
	}

	render() {
		let minbid = this.props.bidder ? ((this.props.highbid|0) + 10) : (this.props.facevalue|0);
		//If you've been outbid, blank the field.
		if (this.refs.bid && (this.refs.bid.value|0) < minbid) this.refs.bid.value = "";
		return <form className="property" onSubmit={this.submit.bind(this)}>
			<h3 style={{backgroundColor: this.props.color, color: this.props.fg || "black"}}>{this.props.name}</h3>
			<p>
				Current high bid:<br />
				{this.props.bidder || "(nobody)"} {this.props.highbid || this.props.facevalue}
			</p>
			<div>
				<input type="number" ref="bid" defaultValue={this.props.bidder ? "" : this.props.facevalue} />
				<input type="submit" value="Bid" />
			</div>
			<div>{this.props.bidder ? <input type="submit" value={"Bid " + minbid} /> : "\xa0"}</div>
		</form>;
	}
})
