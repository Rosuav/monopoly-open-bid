const initial_state = {
	properties: [
		{name: "Vine Street", facevalue: 180, color: "#E0A000"},
		{name: "Mayfair", facevalue: 400, color: "#000090", fg: "white"},
	],
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
