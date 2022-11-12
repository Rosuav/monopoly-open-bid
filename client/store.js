import reducer from './reducer.js';

let state = reducer();
let triggers = [];

export default {
	onchange: f => {triggers.push(f); f(state);},
	dispatch: ev => {state = reducer(state, ev); triggers.forEach(f => f(state));},
};
