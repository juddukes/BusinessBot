// Input listeners
document.getElementById("companySearch").addEventListener("input", searchCompanies);
document.getElementById("statusFilter").addEventListener("change", searchCompanies);
document.getElementById("jurisdictionFilter").addEventListener("change", searchCompanies);
document.getElementById("exportBtn").addEventListener("click", exportPDF);

// Search and render companies
async function searchCompanies() {
  const query = document.getElementById("companySearch").value;
  const status = document.getElementById("statusFilter").value;
  const jurisdiction = document.getElementById("jurisdictionFilter").value;

  const res = await fetch(`/api/search?q=${encodeURIComponent(query)}&status=${encodeURIComponent(status)}&jurisdiction=${encodeURIComponent(jurisdiction)}`);
  const data = await res.json();

  const resultsDiv = document.getElementById("searchResults");
  resultsDiv.innerHTML = "";

  if (data.error) {
    resultsDiv.innerHTML = `<p class="error">Error: ${data.error}</p>`;
    return;
  }

  if (data.length === 0) {
    resultsDiv.innerHTML = `<p>No results found.</p>`;
    return;
  }

  data.forEach(company => {
    const div = document.createElement("div");
    div.className = "company-card";
    div.style = "margin-bottom: 1rem; border: 1px solid #ddd; padding: 10px; border-radius: 6px;";
    div.innerHTML = `
      <h4>${company.name}</h4>
      <p><strong>Status:</strong> ${company.status || "N/A"}</p>
      <p><strong>Jurisdiction:</strong> ${company.jurisdiction || "N/A"}</p>
      <p><strong>Incorporation Date:</strong> ${company.incorporation_date || "N/A"}</p>
      <p><strong>Address:</strong> ${company.address || "N/A"}</p>
      <p><em>${company.summary || ""}</em></p>
      <button onclick="askAdvice('${company.name}', '${company.jurisdiction}')">Get Strategy Advice</button>
    `;
    resultsDiv.appendChild(div);
  });
}

// Pre-fills prompt and triggers AI
function askAdvice(name, industry) {
  const prompt = `I want to compete with or learn from ${name}, a company in the ${industry} industry. What should my strategy be?`;
  document.getElementById("userPrompt").value = prompt;
  askAI();
}

// Calls OpenAI endpoint
function askAI() {
  const prompt = document.getElementById("userPrompt").value;
  const stage = document.getElementById("stage").value;
  const industry = document.getElementById("industry").value;
  const budget = document.getElementById("budget").value;

  document.getElementById("responseBox").textContent = "Thinking...";

  fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, stage, industry, budget })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("responseBox").textContent = data.response;
    })
    .catch(() => {
      document.getElementById("responseBox").textContent = "Error fetching response.";
    });
}

// Exports response as PDF
function exportPDF() {
  const content = document.getElementById("responseBox").textContent;

  fetch("/api/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content })
  })
    .then(res => res.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "business_plan.pdf";
      a.click();
      window.URL.revokeObjectURL(url);
    });
}
