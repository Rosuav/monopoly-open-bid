import {lindt, DOM, on} from "https://rosuav.github.io/choc/factory.js";
const {DIV, H1, LI, P, UL} = lindt; //autoimport
import Property from './property.js';
import Login from './login.js';
import Done from './done.js';

export default function render(state) {
	return DIV([
		state.user && !state.all_done && Done(state),
		H1("Monopoly Open Bidding"),
		P("Place bids on property, yada yada"),
		UL({class: "userlist"}, [
			LI("Funds:"),
			state.users.map(u => LI(u[0] + ": " + u[1])),
		]),
		state.user ? state.order.map(p => Property(state, p, state.properties[p])) : Login(state),
	]);
}
