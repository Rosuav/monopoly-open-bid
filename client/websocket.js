import store from './store';

const socket = new WebSocket("ws://" + window.location.host + "/ws");
socket.onopen = () => {console.log("Socket connection established.");};
socket.onmessage = (ev) => {store.dispatch({type: "WEBSOCKET", data: JSON.parse(ev.data)});};

export default function socksend(type, data) {
	socket.send(JSON.stringify({type, data}));
}
