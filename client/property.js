import React from 'react';
import {connect} from 'react-redux';
import socksend from './websocket';

class Property extends React.Component {
	submit(e) {
		e.preventDefault();
		socksend("bid", {name: this.props.name, value: this.refs.bid.value});
	}

	submitmin(val) {
		socksend("bid", {name: this.props.name, value: val});
	}

	render() {
		let name = <h3 style={{backgroundColor: this.props.color, color: this.props.fg || "black"}}>{this.props.name}</h3>;
		if (this.props.all_done)
		{
			if (!this.props.bidder) return <span />;
			return <div className="property">
				{name}
				<p>{this.props.bidder} ({this.props.highbid})</p>
			</div>;
		}
		let minbid = this.props.bidder ? ((this.props.highbid|0) + 10) : (this.props.facevalue|0);
		//If you've been outbid, blank the field.
		if (this.refs.bid && (this.refs.bid.value|0) < minbid) this.refs.bid.value = "";
		return <form className="property" onSubmit={this.submit.bind(this)}>
			{name}
			<p>
				Current high bid:<br />
				{this.props.bidder || "(nobody)"} {this.props.highbid || this.props.facevalue}
			</p>
			<div>
				<input type="number" ref="bid" defaultValue={this.props.bidder ? "" : this.props.facevalue} />
				<input type="submit" value="Bid" />
			</div>
			<div>{
				this.props.bidder == this.props.user ? "YOURS" :
				this.props.bidder ? <button type="button" onClick={this.submitmin.bind(this, minbid)}>Bid {minbid}</button>
				: "\xa0"
			}</div>
		</form>;
	}
}

export default connect(
	({user, all_done}) => ({user, all_done})
)(Property);
