import React from 'react';
import ReactDOM from 'react-dom';
import MainComponent from './main-component';
import store from './store';
import {Provider} from 'react-redux';

window.socket = new WebSocket("ws://" + window.location.host + "/ws");
socket.onopen = () => {console.log("Socket connection established.");};
socket.onmessage = (ev) => {store.dispatch({type: "WEBSOCKET", data: JSON.parse(ev.data)});};

document.addEventListener('DOMContentLoaded', () =>
	ReactDOM.render(<Provider store={store}>
		<MainComponent />
	</Provider>, document.getElementById('app'))
);
