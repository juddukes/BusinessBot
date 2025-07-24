document.getElementById("companySearch").addEventListener("input", fetchCompanies);
document.getElementById("statusFilter").addEventListener("change", fetchCompanies);
document.getElementById("jurisdictionFilter").addEventListener("change", fetchCompanies);

async function fetchCompanies() {
  const query = document.getElementById("companySearch").value;
  const status = document.getElementById("statusFilter").value;
  const jurisdiction = document.getElementById("jurisdictionFilter").value;

  const res = await fetch(`/api/search?q=${query}&status=${status}&jurisdiction=${jurisdiction}`);
  const data = await res.json();

  const resultsDiv = document.getElementById("searchResults");
  resultsDiv.innerHTML = data.length
    ? data.map(company => `
        <div class="result-item">
          <strong>${company.name}</strong> — ${company.industry} 
          (${company.status}, ${company.jurisdiction})
        </div>`).join("")
    : "<p>No results found.</p>";
}

function askAI() {
  const prompt = document.getElementById("userPrompt").value;
  const sessionId = "default_session"; // optional customization
  document.getElementById("responseBox").textContent = "Thinking...";

  fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, session_id: sessionId })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("responseBox").textContent = data.response;
    })
    .catch(() => {
      document.getElementById("responseBox").textContent = "Error fetching response.";
    });
}
