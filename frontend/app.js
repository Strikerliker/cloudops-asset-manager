// Replace this after deploying the SAM stack.
const API_BASE_URL = "YOUR_API_ENDPOINT";

const form = document.getElementById("assetForm");
const rows = document.getElementById("assetRows");
const message = document.getElementById("message");
const count = document.getElementById("assetCount");

const fields = ["name", "type", "environment", "region", "owner", "status"];

function apiReady() {
  if (API_BASE_URL === "YOUR_API_ENDPOINT") {
    message.textContent = "Deploy the AWS stack, then set API_BASE_URL in frontend/app.js.";
    return false;
  }
  return true;
}

async function loadAssets() {
  if (!apiReady()) return;
  message.textContent = "Loading assets...";
  try {
    const response = await fetch(`${API_BASE_URL}/assets`);
    if (!response.ok) throw new Error("Could not load assets");
    const assets = await response.json();
    renderAssets(assets);
    message.textContent = "";
  } catch (error) {
    message.textContent = error.message;
  }
}

function renderAssets(assets) {
  count.textContent = `${assets.length} asset${assets.length === 1 ? "" : "s"}`;
  rows.innerHTML = "";
  assets.forEach(asset => {
    const tr = document.createElement("tr");
    for (const key of ["name", "type", "environment", "region", "owner", "status"]) {
      const td = document.createElement("td");
      td.textContent = asset[key] || "";
      tr.appendChild(td);
    }
    const actions = document.createElement("td");
    const edit = document.createElement("button");
    edit.textContent = "Edit";
    edit.className = "small secondary";
    edit.onclick = () => editAsset(asset);
    const remove = document.createElement("button");
    remove.textContent = "Delete";
    remove.className = "small danger";
    remove.onclick = () => deleteAsset(asset.assetId, asset.name);
    actions.append(edit, remove);
    tr.appendChild(actions);
    rows.appendChild(tr);
  });
}

function editAsset(asset) {
  document.getElementById("assetId").value = asset.assetId;
  fields.forEach(field => document.getElementById(field).value = asset[field] || "");
  document.getElementById("formTitle").textContent = "Update Asset";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
  form.reset();
  document.getElementById("assetId").value = "";
  document.getElementById("region").value = "us-east-2";
  document.getElementById("formTitle").textContent = "Add Asset";
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (!apiReady()) return;
  const assetId = document.getElementById("assetId").value;
  const payload = Object.fromEntries(fields.map(field => [field, document.getElementById(field).value.trim()]));
  const url = assetId ? `${API_BASE_URL}/assets/${assetId}` : `${API_BASE_URL}/assets`;
  try {
    const response = await fetch(url, {
      method: assetId ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error("Could not save asset");
    resetForm();
    await loadAssets();
  } catch (error) {
    message.textContent = error.message;
  }
});

async function deleteAsset(assetId, name) {
  if (!apiReady() || !confirm(`Delete ${name}?`)) return;
  try {
    const response = await fetch(`${API_BASE_URL}/assets/${assetId}`, { method: "DELETE" });
    if (!response.ok) throw new Error("Could not delete asset");
    await loadAssets();
  } catch (error) {
    message.textContent = error.message;
  }
}

document.getElementById("refreshBtn").onclick = loadAssets;
document.getElementById("cancelBtn").onclick = resetForm;
loadAssets();
