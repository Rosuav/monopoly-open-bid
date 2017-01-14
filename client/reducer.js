const initial_state = {
	properties: {},
	order: [],
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
			let data = action.data;
			console.log("Message from websocket:", data.type);
			switch (data.type) {
				case 'properties':
					return {...state, properties: data.data, order: data.order};
				default: break;
			}
			break;
		default: break;
	}
	return state;
}
