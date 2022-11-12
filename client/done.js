import {lindt, DOM, on} from "https://rosuav.github.io/choc/factory.js";
const {BUTTON} = lindt; //autoimport
import socksend from './websocket.js';

on("click", ".done", e => socksend("done", {}));

export default function render(state) {
	return BUTTON({class: "done"}, [
		state.done ? "Not done yet" : "I'm done!",
		` (${state.done_count||0}/${state.users.length})`,
	]);
}
