
document.getElementById("exportBtn").addEventListener("click", exportPDF);

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

async function getChecklist(stage, industry) {
  const res = await fetch("/api/checklist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ stage, industry })
  });
  const data = await res.json();
  document.getElementById("checklistBox").innerHTML = `<pre>${data.checklist}</pre>`;
}

async function benchmarkCompetitor(name, industry) {
  const res = await fetch("/api/benchmark", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ competitor: name, industry })
  });
  const data = await res.json();
  document.getElementById("responseBox").innerText = data.response;
}