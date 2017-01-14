const initial_state = {
	spam: 'ham',
	paula: 'brillant [sic]',
};

export default function reducer(state=initial_state, action={}) {
	switch (action.type) {
		case 'SPAMIFY_SPAM':
			return {...state, spam: 'spam'};
		case 'HAMIFY_SPAM':
			return {...state, spam: 'ham'};
		case 'REPLACE_PAULA':
			return {...state, paula: action.paula};
		case 'WEBSOCKET':
			console.log("Message from websocket:", action.data);
			break;
		default: break;
	}
	return state;
}
