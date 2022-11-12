import {lindt, DOM, on} from "https://rosuav.github.io/choc/factory.js";
const {DIV, H1, LI, P, UL} = lindt; //autoimport
//import Property from './property';
//import Login from './login';
//import Done from './done';

export default function render(state) {
	return DIV([
		state.user && !state.all_done && "Done() goes here",
		H1("Monopoly Open Bidding"),
		P("Place bids on property, yada yada"),
		UL({class: "userlist"}, [
			LI("Funds:"),
			state.users.map(u => LI(u[0] + ": " + u[1])),
			state.user ? state.order.map(p => "Property(state, p, state.props.properties[p])") : "Login()",
		]),
	]);
}
