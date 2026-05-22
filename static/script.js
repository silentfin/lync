async function shortenUrl() {
  const url = document.getElementById("urlInput").value;

  const response = await fetch("/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: url }),
  });

  const data = await response.json();
  const shortUrl = `${window.location.origin}/${data.short_code}`;
  const longUrl = `${data.url}`;

  document.getElementById("result").innerHTML =
    `Long URL: <a href="${longUrl}">${longUrl}</a><br>
		 Short URL: <a href="${shortUrl}">${shortUrl}</a><br>
		 URL stats: <a href="${shortUrl}/stats">${shortUrl}/stats</a><br>`;
}
