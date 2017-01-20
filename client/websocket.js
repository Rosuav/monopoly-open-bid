import store from './store';

//TODO: Establish a connection only when we join a room?
//Or establish a connection, and then choose a room over it?
const protocol = window.location.protocol == "https:" ? "wss://" : "ws://";
const socket = new WebSocket(protocol + window.location.host + "/ws");
socket.onopen = () => {console.log("Socket connection established.");};
socket.onmessage = (ev) => {store.dispatch({type: "WEBSOCKET", data: JSON.parse(ev.data)});};

export default function socksend(type, data) {
	socket.send(JSON.stringify({type, data}));
}
