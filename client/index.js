import {lindt, replace_content, DOM, on} from "https://rosuav.github.io/choc/factory.js";
const {} = lindt; //autoimport
import MainComponent from './main-component.js';
import store from './store.js';
import './websocket.js';

document.addEventListener('DOMContentLoaded', () =>
	store.onchange(state => replace_content("#app", MainComponent(state)))
);
