function askAI() {
  const prompt = document.getElementById("userPrompt").value;
  document.getElementById("responseBox").textContent = "Thinking...";

  fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("responseBox").textContent = data.response;
  })
  .catch(() => {
    document.getElementById("responseBox").textContent = "Error fetching response.";
  });
}

function searchCompanies() {
  const query = document.getElementById("searchInput").value;
  fetch(`/api/search?q=${query}`)
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById("resultsList");
      list.innerHTML = "";
      data.forEach(item => {
        const li = document.createElement("li");
        li.textContent = `${item.name} — ${item.industry} (${item.status})`;
        list.appendChild(li);
      });
    });
}
