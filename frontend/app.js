// Helper function for POST requests
async function postForm(url, form) {
  const resp = await fetch(url, { method: "POST", body: form });
  return resp.json();
}

// Show file info and preview when an image is selected
document.getElementById("file").addEventListener("change", function(e) {
  const fileInfo = document.getElementById("fileInfo");
  const file = e.target.files[0];
  if (!file) {
    fileInfo.classList.add("hidden");
    fileInfo.innerHTML = "";
    return;
  }
  let html = `<b>Image selected:</b> ${file.name}`;
  if (file.type.startsWith("image/")) {
    const reader = new FileReader();
    reader.onload = function(ev) {
      html += `<br><img src='${ev.target.result}' alt='preview' style='max-width:120px;max-height:120px;margin-top:8px;border-radius:8px;box-shadow:0 2px 8px #0001;'>`;
      fileInfo.innerHTML = html;
      fileInfo.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
  } else {
    fileInfo.innerHTML = html;
    fileInfo.classList.remove("hidden");
  }
});

// Handle image upload
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("file");
  if (!fileInput.files[0]) return alert("Select an image first");

  const form = new FormData();
  form.append("file", fileInput.files[0]);

  try {
  const res = await postForm("http://127.0.0.1:8080/api/analyze", form);

    // Show analysis results with color name and swatch
    document.getElementById("analysis").classList.remove("hidden");
    let html = `<b>Item:</b> ${res.item_name || "Unknown"}<br>`;
    html += `<b>Condition:</b> ${res.condition || "Unknown"}<br>`;
    if (res.color_hex && res.color_hex !== "unknown") {
      html += `<b>Color:</b> <span style="display:inline-block;width:20px;height:20px;background:${res.color_hex};border:1px solid #ccc;vertical-align:middle;"></span> (${res.color_hex})<br>`;
    }
    html += `<b>Confidence:</b> ${(res.score ? (res.score*100).toFixed(1) : "?")} %`;
    document.getElementById("analysis").innerHTML = html;

    // Fill hidden form fields for action
    document.getElementById("item_name").value = res.item_name || "";
    document.getElementById("condition").value = res.condition || "";

    // Show action buttons
    document.getElementById("actions").classList.remove("hidden");
    document.getElementById("output").classList.add("hidden");

  } catch (err) {
    alert("Error analyzing image: " + err);
  }
});

// Handle action buttons (Sell, Donate, Recycle, Style)
document.querySelectorAll(".actionBtn").forEach(btn => {
  btn.addEventListener("click", async (e) => {
    const action = e.target.dataset.action;
    const fileInput = document.getElementById("file");

    const form = new FormData();
    if (fileInput.files[0]) form.append("file", fileInput.files[0]);
    form.append("action", action);

    const itemName = document.getElementById("item_name").value;
    const condition = document.getElementById("condition").value;
    if (itemName) form.append("item_name", itemName);
    if (condition) form.append("condition", condition);
    // Add color and color_name from analysis panel if available
    const analysisPanel = document.getElementById("analysis");
    if (analysisPanel && analysisPanel.innerHTML) {
      // Try to extract color and color_name from the HTML
      const colorMatch = analysisPanel.innerHTML.match(/\((#[0-9a-fA-F]{6})\)/);
      const colorNameMatch = analysisPanel.innerHTML.match(/Color:<\/b> ([^ <]+)/);
      if (colorMatch && colorMatch[1]) form.append("color", colorMatch[1]);
      if (colorNameMatch && colorNameMatch[1]) form.append("color_name", colorNameMatch[1]);
    }

    // Add geolocation if available
    if (navigator.geolocation) {
      try {
        const pos = await new Promise((resolve, reject) =>
          navigator.geolocation.getCurrentPosition(resolve, reject)
        );
        form.append("location", JSON.stringify({ lat: pos.coords.latitude, lng: pos.coords.longitude }));
      } catch (err) {}
    }

    try {
      const res = await postForm("http://127.0.0.1:8080/api/action", form);

      // Enhanced output panel with card style and icons
      const outputPanel = document.getElementById("output");
      outputPanel.classList.remove("hidden");
      let html = `<div class='output-card'>`;
      // Action icon
      const actionIcons = {
        sell: "💸",
        donate: "🤝",
        recycle: "♻️",
        style: "✨"
      };
      if (res && res.action) {
        const icon = actionIcons[res.action] || "🛠️";
        html += `<div class='output-action'><span class='output-icon'>${icon}</span> <span class='output-action-label'>${res.action.charAt(0).toUpperCase() + res.action.slice(1)}</span></div>`;
      }
      if (res && res.result) {
        html += `<div class='output-response'><b>Agent Response:</b>`;
        if (Array.isArray(res.result)) {
          // Format array as a styled list
          html += `<ol class='output-list'>`;
          for (const item of res.result) {
            html += `<li>${item}</li>`;
          }
          html += `</ol>`;
        } else if (typeof res.result === "string") {
          html += `<div class='output-message'>${res.result}</div>`;
        } else if (typeof res.result === "object") {
          html += `<ul class='output-list'>`;
          for (const [key, value] of Object.entries(res.result)) {
            html += `<li><b>${key.replace(/_/g, ' ')}:</b> ${typeof value === "object" ? JSON.stringify(value) : value}</li>`;
          }
          html += `</ul>`;
        } else {
          html += `<div class='output-message'>${res.result}</div>`;
        }
        html += `</div>`;
      } else {
        html += `<div style='color:#b00;'>No response from agent.</div>`;
      }
      html += `</div>`;
      outputPanel.innerHTML = html;

    } catch (err) {
      alert("Error performing action: " + err);
    }
  });
});
