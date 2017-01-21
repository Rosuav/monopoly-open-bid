const initial_state = {
	properties: {},
	order: [],
	users: [],
	funds: 0,
};

export default function reducer(state=initial_state, action={}) {
	switch (action.type) {
		case 'WEBSOCKET':
			let data = action.data;
			console.log("Message from websocket:", data.type);
			switch (data.type) {
				case 'properties':
					return {...state, properties: data.data, order: data.order};
				case 'property':
					return {...state, properties: {...state.properties, [data.name]: data.data}};
				case 'login':
					return {...state, user: data.name};
				case 'users':
					return {...state, users: data.users, funds: data.funds, done_count: data.done_count, all_done: data.all_done};
				default: break;
			}
			break;
		default: break;
	}
	return state;
}
