import {lindt, DOM, on} from "https://rosuav.github.io/choc/factory.js";
const {BR, BUTTON, DIV, FORM, H3, INPUT, P, SPAN} = lindt; //autoimport
import socksend from './websocket.js';

on("submit", ".property", e => {
	e.preventDefault();
	socksend("bid", {name: e.match.dataset.name, value: e.match.elements.bid.value});
});

on("click", ".submitmin", e => socksend("bid", {name: e.match.closest("[data-name]").dataset.name, value: e.match.value}));

export default function render(state, property, info) {
	let name = H3({style: "background-color: " + info.color + "; color: " + (info.fg || "black")}, property);
	if (state.all_done) {
		if (!info.bidder) return SPAN(); //Might be able to replace this with "return null"
		return DIV({class: "property"}, [
			name,
			P(info.bidder + " (" + info.highbid + ")"),
		]);
	}
	let minbid = info.bidder ? ((info.highbid|0) + 10) : (info.facevalue|0);
	//FIXME: If you've been outbid, blank the field.
	//if (this.refs.bid && (this.refs.bid.value|0) < minbid) this.refs.bid.value = "";
	return FORM({class: "property", "data-name": property}, [
		name,
		P([
			"Current high bid:", BR(),
			info.bidder || "(nobody)",
			" ", info.highbid || info.facevalue,
		]),
		DIV([
			INPUT({type: "number", name: "bid", value: info.bidder ? "" : info.facevalue}),
			INPUT({type: "submit", value: "Bid"}),
		]),
		DIV([
			info.bidder == state.user ? "YOURS" :
			info.bidder ? BUTTON({type: "button", value: minbid}, "Bid " + minbid)
			: "\xa0"
		]),
	]);
}
