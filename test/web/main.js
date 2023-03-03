async function clicked() {
	var data = {
		"value": 10,
		"data": "Hello world"
	};

	const res = await fetch("http://localhost:5050/", {
		method: 'POST', 
		headers: {
			"Content-Type": "text/plain",
			"Accept": "application/json"
		},
		body: JSON.stringify(data)
	});
	console.log(res);
}
