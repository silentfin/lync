async function shortenUrl() {
	const url = document.getElementById('urlInput').value;

	const response = await fetch('http://localhost:8000/', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ url: url })
	});

	const data = await response.json();
	const shortUrl = `http://localhost:8000/${data.short_code}`;

	document.getElementById('result').innerHTML =
		`Short URL: <a href="${shortUrl}">${shortUrl}</a>`;
}
