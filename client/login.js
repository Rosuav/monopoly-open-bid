import {lindt, DOM, on} from "https://rosuav.github.io/choc/factory.js";
const {BR, FORM, H3, INPUT, LABEL} = lindt; //autoimport
import socksend from './websocket.js';

on("submit", "#loginform", e => {
	e.preventDefault();
	socksend("login", {room: e.match.elements.room.value, name: e.match.elements.name.value});
});

export default function render(state) {
	return FORM({id: "loginform"}, [
		H3("Log in"),
		LABEL(["Room: ", INPUT({name: "room"})]), BR(),
		LABEL(["Name: ", INPUT({name: "name"})]), BR(),
		INPUT({type: "submit", value: "Register/log in"}),
	]);
}
