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
