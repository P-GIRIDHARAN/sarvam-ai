// DocuPulse AI - Main Frontend Application Logic
// Powered by Sarvam AI

let currentDocId = null;
let allDocuments = [];

document.addEventListener("DOMContentLoaded", () => {
  initApp();
  setupDragAndDrop();
});

async function initApp() {
  await checkHealth();
  await refreshDashboard();
  await refreshDataset();
  await refreshWorkflows();
}

// --- Connectivity & Health ---
async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const badge = document.getElementById("sarvam-status-badge");
    const text = document.getElementById("sarvam-status-text");

    if (data.sarvam_ai && data.sarvam_ai.status === "connected") {
      badge.style.background = "rgba(16, 185, 129, 0.15)";
      badge.style.borderColor = "rgba(16, 185, 129, 0.4)";
      badge.style.color = "#34d399";
      text.innerText = `Sarvam AI: Online (${data.sarvam_ai.latency_ms}ms)`;
    } else {
      badge.style.background = "rgba(244, 63, 94, 0.15)";
      badge.style.borderColor = "rgba(244, 63, 94, 0.4)";
      badge.style.color = "#fb7185";
      text.innerText = `Sarvam AI: ${data.sarvam_ai?.status || "Offline"}`;
    }
  } catch (err) {
    console.error("Health check error:", err);
  }
}

// --- Tab Navigation ---
function switchTab(tabId) {
  document.querySelectorAll(".nav-tab").forEach(tab => tab.classList.remove("active"));
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));

  const targetTab = document.getElementById(tabId);
  if (targetTab) targetTab.classList.add("active");

  const viewMap = {
    "dashboard-tab": "view-dashboard",
    "ingest-tab": "view-ingest",
    "query-tab": "view-query",
    "dataset-tab": "view-dataset",
    "workflow-tab": "view-workflow"
  };

  const targetView = document.getElementById(viewMap[tabId]);
  if (targetView) targetView.classList.add("active");

  if (tabId === "dashboard-tab") refreshDashboard();
  if (tabId === "dataset-tab") refreshDataset();
  if (tabId === "workflow-tab") refreshWorkflows();
}

// --- Dashboard & Analytics ---
async function refreshDashboard() {
  try {
    const res = await fetch("/api/analytics/dashboard");
    const data = await res.json();
    const kpis = data.kpis;

    document.getElementById("kpi-total-docs").innerText = kpis.total_documents;
    document.getElementById("kpi-total-vol").innerText = `₹ ${kpis.total_financial_volume.toLocaleString('en-IN')}`;
    document.getElementById("kpi-accuracy").innerText = `${kpis.avg_confidence_score}%`;
    document.getElementById("kpi-pending").innerText = kpis.pending_actions;
    document.getElementById("kpi-risks").innerText = kpis.high_risk_alerts;

    document.getElementById("total-docs-badge").innerText = kpis.total_documents;
    document.getElementById("pending-badge").innerText = kpis.pending_actions;

    renderVendorBars(data.top_vendors, kpis.total_financial_volume);
    renderTypeDonut(data.type_distribution);
    renderLanguageSplit(data.language_split);
    renderDashboardAlerts(data.recent_alerts);
  } catch (err) {
    console.error("Dashboard refresh error:", err);
  }
}

function renderVendorBars(vendors, totalVolume) {
  const container = document.getElementById("vendor-bars-container");
  if (!vendors || vendors.length === 0) {
    container.innerHTML = `<p style="color:var(--text-dim); text-align:center; padding:1.5rem;">No vendor data recorded yet.</p>`;
    return;
  }

  const maxSpend = Math.max(...vendors.map(v => v.spend || 0), 1);
  container.innerHTML = vendors.map(v => {
    const pct = Math.min(100, Math.round(((v.spend || 0) / maxSpend) * 100));
    return `
      <div class="data-bar-item">
        <div class="bar-labels">
          <span class="bar-name">${escapeHtml(v.entity_name)}</span>
          <span class="bar-val">₹ ${(v.spend || 0).toLocaleString('en-IN')} (${v.doc_count} docs)</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${pct}%;"></div>
        </div>
      </div>
    `;
  }).join("");
}

function renderTypeDonut(types) {
  const container = document.getElementById("type-donut-container");
  if (!types || types.length === 0) {
    container.innerHTML = `<p style="color:var(--text-dim); text-align:center;">No classifications available.</p>`;
    return;
  }

  const total = types.reduce((acc, t) => acc + t.count, 0) || 1;
  container.innerHTML = types.map(t => {
    const pct = Math.round((t.count / total) * 100);
    return `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:0.6rem 0.85rem; background:rgba(255,255,255,0.03); border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
        <div style="display:flex; align-items:center; gap:0.6rem;">
          <span class="badge badge-type">${t.doc_type}</span>
          <span style="font-size:0.82rem; color:var(--text-muted);">${t.count} items (${pct}%)</span>
        </div>
        <span style="font-size:0.85rem; font-weight:700; font-family:var(--font-mono);">₹ ${(t.total_val || 0).toLocaleString('en-IN')}</span>
      </div>
    `;
  }).join("");
}

function renderLanguageSplit(languages) {
  const container = document.getElementById("language-bars-container");
  if (!languages || languages.length === 0) {
    container.innerHTML = `<p style="color:var(--text-dim); text-align:center;">No language data yet.</p>`;
    return;
  }

  container.innerHTML = languages.map(l => {
    return `
      <div class="data-bar-item">
        <div class="bar-labels">
          <span class="bar-name">${escapeHtml(l.detected_language)}</span>
          <span class="bar-val">${l.count} docs • Avg Conf: ${Math.round(l.avg_conf)}%</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="width:${Math.min(100, Math.round(l.avg_conf))}%; background:linear-gradient(90deg, #10b981, #06b6d4);"></div>
        </div>
      </div>
    `;
  }).join("");
}

function renderDashboardAlerts(alerts) {
  const feed = document.getElementById("dashboard-alerts-feed");
  if (!alerts || alerts.length === 0) {
    feed.innerHTML = `<p style="color:var(--text-dim); text-align:center; padding:1rem;">All workflows nominal. No active alerts.</p>`;
    return;
  }

  feed.innerHTML = alerts.map(a => {
    const sevClass = a.severity === 'CRITICAL' ? 'badge-flagged' : (a.severity === 'HIGH' ? 'badge-pending' : 'badge-type');
    return `
      <div style="padding:0.75rem 1rem; border-radius:var(--radius-sm); background:rgba(255,255,255,0.02); border:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.2rem;">
            <span class="badge ${sevClass}">${a.severity}</span>
            <span style="font-size:0.82rem; font-weight:600; color:#fff;">${escapeHtml(a.rule_name)}</span>
          </div>
          <p style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(a.action_taken)}</p>
        </div>
        <button class="btn btn-secondary" style="padding:0.25rem 0.6rem; font-size:0.72rem;" onclick="inspectDocument(${a.document_id})">
          Inspect
        </button>
      </div>
    `;
  }).join("");
}

// --- Document Ingestion ---
function setupDragAndDrop() {
  const dropZone = document.getElementById("file-drop-zone");
  if (!dropZone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, e => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, e => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
    });
  });

  dropZone.addEventListener('drop', e => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadFile(files[0]);
    }
  });
}

function handleFileSelected(event) {
  const file = event.target.files[0];
  if (file) {
    uploadFile(file);
  }
}

async function uploadFile(file) {
  const progressBox = document.getElementById("upload-progress-box");
  const title = document.getElementById("upload-status-title");
  const pct = document.getElementById("upload-status-pct");
  const bar = document.getElementById("upload-progress-bar");
  const sub = document.getElementById("upload-status-sub");

  progressBox.style.display = "block";
  title.innerText = `Ingesting ${file.name}...`;
  pct.innerText = "25%";
  bar.style.width = "25%";
  sub.innerText = "Parsing document layout & extracting text streams...";

  const formData = new FormData();
  formData.append("file", file);
  formData.append("doc_hint", document.getElementById("upload-doc-hint").value);
  formData.append("language", document.getElementById("upload-doc-language").value);

  setTimeout(() => {
    pct.innerText = "60%";
    bar.style.width = "60%";
    sub.innerText = "Sending to Sarvam AI (Sarvam-105b) for schema extraction...";
  }, 1000);

  try {
    const res = await fetch("/api/documents/upload", {
      method: "POST",
      body: formData
    });

    pct.innerText = "90%";
    bar.style.width = "90%";
    sub.innerText = "Evaluating workflow triggers & indexing queryable dataset...";

    const data = await res.json();
    if (data.success) {
      pct.innerText = "100%";
      bar.style.width = "100%";
      title.innerText = "Document Processed & Indexed Successfully!";
      sub.innerText = `Extracted ${data.structured_data.doc_type} with ${data.structured_data.confidence_score}% confidence.`;

      setTimeout(() => {
        progressBox.style.display = "none";
        inspectDocument(data.document_id);
        refreshDashboard();
        refreshDataset();
      }, 1200);
    } else {
      title.innerText = "Processing Issue Encountered";
      sub.innerText = data.detail || "Unable to extract document.";
    }
  } catch (err) {
    title.innerText = "Upload Failed";
    sub.innerText = err.message;
  }
}

async function loadSampleDocs(event) {
  if (event) event.preventDefault();
  try {
    const res = await fetch("/api/documents/load-samples", { method: "POST" });
    const data = await res.json();
    alert(`Success: ${data.message}`);
    await refreshDashboard();
    await refreshDataset();
    await refreshWorkflows();
  } catch (err) {
    alert(`Error loading samples: ${err.message}`);
  }
}

function viewSampleDoc(sampleIndex) {
  inspectDocument(sampleIndex);
}

// --- Unified Query Explorer (Sarvam AI Agent) ---
function fillQuery(text) {
  document.getElementById("agent-query-input").value = text;
  submitAgentQuery();
}

async function submitAgentQuery() {
  const input = document.getElementById("agent-query-input");
  const query = input.value.trim();
  if (!query) return;

  const btn = document.getElementById("query-submit-button");
  const wrapper = document.getElementById("query-result-wrapper");
  const responseText = document.getElementById("agent-response-text");
  const matchedGrid = document.getElementById("matched-docs-grid");

  btn.disabled = true;
  btn.innerHTML = `<span>⏳</span> Reasoning...`;
  wrapper.style.display = "block";
  responseText.innerHTML = `<p style="color:var(--text-muted); font-style:italic;">Querying unified dataset and synthesizing insights with Sarvam-105b...</p>`;
  matchedGrid.innerHTML = "";

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query })
    });
    const data = await res.json();

    // Render formatted markdown
    responseText.innerHTML = formatMarkdown(data.answer);

    // Render matched references
    if (data.matched_documents && data.matched_documents.length > 0) {
      matchedGrid.innerHTML = data.matched_documents.map(d => `
        <div class="glass-panel" style="padding:1rem; cursor:pointer;" onclick="inspectDocument(${d.id})">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
            <span class="badge badge-type">${d.doc_type}</span>
            <span style="font-size:0.75rem; color:var(--text-dim);">#${d.id}</span>
          </div>
          <h4 style="font-size:0.88rem; font-weight:700; color:#fff;">${escapeHtml(d.title)}</h4>
          <p style="font-size:0.78rem; color:var(--text-muted); margin-top:2px;">${escapeHtml(d.entity_name)}</p>
          <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:0.75rem;">
            <span style="font-weight:700; font-family:var(--font-mono); font-size:0.9rem;">${d.currency} ${d.total_amount?.toLocaleString('en-IN')}</span>
            <span style="font-size:0.75rem; color:var(--emerald);">Conf: ${Math.round(d.confidence_score)}%</span>
          </div>
        </div>
      `).join("");
    } else {
      matchedGrid.innerHTML = `<p style="font-size:0.8rem; color:var(--text-dim);">No specific document links generated for this query.</p>`;
    }
  } catch (err) {
    responseText.innerHTML = `<p style="color:var(--rose);">Query error: ${err.message}</p>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>✨</span> Ask Agent`;
  }
}

// --- Unified Dataset Table ---
async function refreshDataset() {
  const typeFilter = document.getElementById("filter-type")?.value || "";
  const statusFilter = document.getElementById("filter-status")?.value || "";
  const searchFilter = document.getElementById("table-search-input")?.value || "";

  let url = `/api/documents?limit=200`;
  if (typeFilter) url += `&doc_type=${encodeURIComponent(typeFilter)}`;
  if (statusFilter) url += `&status=${encodeURIComponent(statusFilter)}`;
  if (searchFilter) url += `&search=${encodeURIComponent(searchFilter)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    allDocuments = data.documents;

    const tbody = document.getElementById("dataset-table-body");
    if (!allDocuments || allDocuments.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:2rem; color:var(--text-dim);">No documents match current filters.</td></tr>`;
      return;
    }

    tbody.innerHTML = allDocuments.map(d => {
      const statusBadge = d.workflow_status === 'APPROVED' ? 'badge-approved' : 
                         (d.workflow_status.includes('FLAG') ? 'badge-flagged' : 'badge-pending');
      const riskBadge = d.risk_level === 'HIGH' ? 'badge-flagged' : (d.risk_level === 'MEDIUM' ? 'badge-pending' : 'badge-approved');

      return `
        <tr>
          <td><span style="font-family:var(--font-mono); font-weight:600; color:var(--primary-light);">#${d.id}</span></td>
          <td><span class="badge badge-type">${d.doc_type}</span></td>
          <td>
            <div style="font-weight:600; color:#fff;">${escapeHtml(d.title)}</div>
            <div style="font-size:0.75rem; color:var(--text-dim);">${escapeHtml(d.entity_name || 'N/A')}</div>
          </td>
          <td><span style="font-family:var(--font-mono); font-size:0.78rem;">${escapeHtml(d.document_number || 'N/A')}</span></td>
          <td style="font-family:var(--font-mono); font-weight:700;">
            ${d.currency} ${Number(d.total_amount || 0).toLocaleString('en-IN', {minimumFractionDigits: 2})}
          </td>
          <td>
            <div style="display:flex; align-items:center; gap:0.4rem;">
              <span style="font-size:0.8rem; font-weight:600;">${Math.round(d.confidence_score)}%</span>
            </div>
          </td>
          <td><span style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(d.detected_language)}</span></td>
          <td><span class="badge ${riskBadge}">${d.risk_level}</span></td>
          <td><span class="badge ${statusBadge}">${d.workflow_status.replace('_', ' ')}</span></td>
          <td style="text-align:right;">
            <button class="btn btn-secondary" style="padding:0.3rem 0.65rem; font-size:0.75rem;" onclick="inspectDocument(${d.id})">
              Inspect
            </button>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.error("Dataset fetch error:", err);
  }
}

function applyDatasetFilters() {
  refreshDataset();
}

function exportData(format) {
  if (format === 'csv') {
    window.location.href = "/api/analytics/export/csv";
  } else {
    window.open("/api/analytics/export/json", "_blank");
  }
}

// --- Workflows & Automation Studio ---
async function refreshWorkflows() {
  try {
    // 1. Fetch rules
    const rulesRes = await fetch("/api/workflows/rules");
    const rulesData = await rulesRes.json();
    const rulesContainer = document.getElementById("rules-container");

    rulesContainer.innerHTML = rulesData.rules.map(r => `
      <div class="glass-panel rule-card">
        <div class="rule-header">
          <div>
            <div class="rule-title">${escapeHtml(r.rule_name)}</div>
            <span class="badge ${r.severity === 'CRITICAL' ? 'badge-flagged' : (r.severity === 'HIGH' ? 'badge-pending' : 'badge-type')}" style="margin-top:4px;">
              ${r.severity}
            </span>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" ${r.is_active ? 'checked' : ''} onchange="toggleRule(${r.id}, this.checked)">
            <span class="slider"></span>
          </label>
        </div>
        <p style="font-size:0.78rem; color:var(--text-muted);">${escapeHtml(r.description)}</p>
        <div style="font-size:0.72rem; font-family:var(--font-mono); color:var(--primary-light); background:rgba(0,0,0,0.25); padding:0.4rem 0.6rem; border-radius:4px;">
          Trigger: ${escapeHtml(r.trigger_condition)}
        </div>
      </div>
    `).join("");

    // 2. Fetch pending approvals queue
    const docsRes = await fetch("/api/documents?limit=100");
    const docsData = await docsRes.json();
    const pendingDocs = docsData.documents.filter(d => d.workflow_status.includes('PENDING') || d.workflow_status.includes('FLAGGED'));
    const approvalsTable = document.getElementById("approvals-table-body");

    if (pendingDocs.length === 0) {
      approvalsTable.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:2rem; color:var(--text-dim);">No pending items in approval queue. All up to date!</td></tr>`;
    } else {
      approvalsTable.innerHTML = pendingDocs.map(d => `
        <tr>
          <td><span style="font-family:var(--font-mono); font-weight:600; color:var(--primary-light);">#${d.id}</span></td>
          <td><span class="badge badge-type">${d.doc_type}</span></td>
          <td><div style="font-weight:600; color:#fff;">${escapeHtml(d.entity_name || d.title)}</div></td>
          <td style="font-family:var(--font-mono); font-weight:700;">${d.currency} ${Number(d.total_amount || 0).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
          <td><span style="font-size:0.75rem; color:var(--amber);">${d.workflow_status.replace('_', ' ')}</span></td>
          <td><span class="badge ${d.risk_level === 'HIGH' ? 'badge-flagged' : 'badge-pending'}">${d.risk_level}</span></td>
          <td><span style="font-size:0.75rem; color:var(--text-dim);">${d.date}</span></td>
          <td style="text-align:right;">
            <div style="display:inline-flex; gap:0.4rem;">
              <button class="btn btn-success" style="padding:0.25rem 0.6rem; font-size:0.75rem;" onclick="performWorkflowAction(${d.id}, 'APPROVED')">
                Approve
              </button>
              <button class="btn btn-danger" style="padding:0.25rem 0.6rem; font-size:0.75rem;" onclick="performWorkflowAction(${d.id}, 'REJECTED')">
                Reject
              </button>
            </div>
          </td>
        </tr>
      `).join("");
    }

    // 3. Fetch audit logs
    const alertsRes = await fetch("/api/workflows/alerts");
    const alertsData = await alertsRes.json();
    const alertsContainer = document.getElementById("full-alerts-list");

    alertsContainer.innerHTML = alertsData.alerts.map(a => `
      <div style="padding:0.85rem 1.1rem; border-radius:var(--radius-sm); background:rgba(255,255,255,0.02); border:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.2rem;">
            <span class="badge ${a.severity === 'CRITICAL' ? 'badge-flagged' : (a.severity === 'HIGH' ? 'badge-pending' : 'badge-type')}">${a.severity}</span>
            <span style="font-weight:700; font-size:0.85rem; color:#fff;">${escapeHtml(a.rule_name)}</span>
            <span style="font-size:0.72rem; color:var(--text-dim);">Doc #${a.document_id}</span>
          </div>
          <p style="font-size:0.78rem; color:var(--text-muted);">${escapeHtml(a.trigger_event)}</p>
          <p style="font-size:0.72rem; color:var(--primary-light); margin-top:2px;">Action: ${escapeHtml(a.action_taken)}</p>
        </div>
        <div style="text-align:right;">
          <span style="font-size:0.72rem; color:var(--text-dim);">${a.created_at}</span>
          <br>
          <span class="badge ${a.status === 'RESOLVED' ? 'badge-approved' : 'badge-pending'}" style="margin-top:4px;">${a.status}</span>
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.error("Workflow refresh error:", err);
  }
}

async function toggleRule(ruleId, isActive) {
  try {
    await fetch(`/api/workflows/rules/${ruleId}/toggle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_active: isActive })
    });
  } catch (err) {
    console.error("Toggle rule error:", err);
  }
}

async function performWorkflowAction(docId, status) {
  try {
    const res = await fetch(`/api/documents/${docId}/workflow`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: status,
        approved_by: "Executive Approver (UI)",
        notes: `Action marked as ${status} via Executive Workflow Center.`
      })
    });
    if (res.ok) {
      await refreshWorkflows();
      await refreshDashboard();
      await refreshDataset();
    }
  } catch (err) {
    alert(`Workflow action error: ${err.message}`);
  }
}

// --- Side Inspector Drawer (Human-in-the-Loop) ---
async function inspectDocument(docId) {
  currentDocId = docId;
  const drawer = document.getElementById("inspector-drawer");
  const overlay = document.getElementById("inspector-overlay");

  drawer.classList.add("open");
  overlay.classList.add("active");

  try {
    const res = await fetch(`/api/documents/${docId}`);
    const doc = await res.json();

    document.getElementById("drawer-title").innerText = doc.title || "Document Details";
    document.getElementById("drawer-subtitle").innerText = `ID: #${doc.id} • Type: ${doc.doc_type} • Status: ${doc.workflow_status}`;
    document.getElementById("drawer-confidence").innerText = `${Math.round(doc.confidence_score)}%`;
    
    const riskEl = document.getElementById("drawer-risk");
    riskEl.innerText = doc.risk_level;
    riskEl.style.color = doc.risk_level === 'HIGH' ? 'var(--rose)' : (doc.risk_level === 'MEDIUM' ? 'var(--amber)' : 'var(--emerald)');

    // Populate editable fields
    document.getElementById("edit-entity").value = doc.entity_name || "";
    document.getElementById("edit-doc-num").value = doc.document_number || "";
    document.getElementById("edit-gstin").value = doc.gstin_tax_id || "";
    document.getElementById("edit-subtotal").value = doc.subtotal || 0;
    document.getElementById("edit-tax").value = doc.tax_amount || 0;
    document.getElementById("edit-total").value = doc.total_amount || 0;
    document.getElementById("edit-date").value = doc.date || "";
    document.getElementById("edit-due-date").value = doc.due_date || "";

    // Reset translation box
    document.getElementById("translation-result-box").innerText = "Click Translate to view document summary in target Indic language.";

    // Render line items
    const lineItemsBody = document.getElementById("drawer-line-items");
    if (doc.line_items && doc.line_items.length > 0) {
      lineItemsBody.innerHTML = doc.line_items.map(item => `
        <tr>
          <td>${escapeHtml(item.description)}</td>
          <td>${item.quantity}</td>
          <td>${item.unit_price?.toLocaleString('en-IN')}</td>
          <td style="font-weight:600; font-family:var(--font-mono);">${item.total?.toLocaleString('en-IN')}</td>
        </tr>
      `).join("");
    } else {
      lineItemsBody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--text-dim);">No tabular line items detected.</td></tr>`;
    }

    // Render Raw JSON
    const structured = JSON.parse(doc.structured_json || "{}");
    document.getElementById("drawer-json").innerText = JSON.stringify(structured, null, 2);

  } catch (err) {
    console.error("Inspector fetch error:", err);
  }
}

function closeInspector() {
  document.getElementById("inspector-drawer").classList.remove("open");
  document.getElementById("inspector-overlay").classList.remove("active");
  currentDocId = null;
}

async function triggerTranslation() {
  if (!currentDocId) return;
  const lang = document.getElementById("translate-lang-select").value;
  const box = document.getElementById("translation-result-box");
  box.innerHTML = `<span style="color:var(--primary-light);">Translating via Sarvam AI Indic API...</span>`;

  try {
    const res = await fetch(`/api/documents/${currentDocId}/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_language: lang })
    });
    const data = await res.json();
    box.innerHTML = `
      <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:0.25rem;">Translation (${data.target_language}):</div>
      <div style="font-size:0.92rem; font-weight:600; color:#fff;">${escapeHtml(data.translated)}</div>
    `;
  } catch (err) {
    box.innerText = `Translation error: ${err.message}`;
  }
}

async function saveFieldChanges() {
  if (!currentDocId) return;
  const updated = {
    entity_name: document.getElementById("edit-entity").value,
    document_number: document.getElementById("edit-doc-num").value,
    gstin_tax_id: document.getElementById("edit-gstin").value,
    subtotal: parseFloat(document.getElementById("edit-subtotal").value) || 0,
    tax_amount: parseFloat(document.getElementById("edit-tax").value) || 0,
    total_amount: parseFloat(document.getElementById("edit-total").value) || 0,
    date: document.getElementById("edit-date").value,
    due_date: document.getElementById("edit-due-date").value
  };

  try {
    const res = await fetch(`/api/documents/${currentDocId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated)
    });
    if (res.ok) {
      alert("Extracted fields updated successfully.");
      await refreshDataset();
      await refreshDashboard();
    }
  } catch (err) {
    alert(`Failed to save changes: ${err.message}`);
  }
}

async function executeDrawerAction(status) {
  if (!currentDocId) return;
  await performWorkflowAction(currentDocId, status);
  closeInspector();
}

// --- Settings Modal ---
function openSettingsModal() {
  document.getElementById("settings-modal").style.display = "block";
  document.getElementById("settings-overlay").classList.add("active");
}

function closeSettingsModal() {
  document.getElementById("settings-modal").style.display = "none";
  document.getElementById("settings-overlay").classList.remove("active");
}

async function testApiKey() {
  const resultBox = document.getElementById("settings-test-result");
  resultBox.style.display = "block";
  resultBox.style.background = "rgba(99, 102, 241, 0.1)";
  resultBox.style.color = "var(--primary-light)";
  resultBox.innerText = "Pinging Sarvam AI endpoints...";

  const key = document.getElementById("settings-api-key").value.trim();
  try {
    const res = await fetch("/api/settings/sarvam", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: key })
    });
    const data = await res.json();
    if (data.success) {
      resultBox.style.background = "rgba(16, 185, 129, 0.15)";
      resultBox.style.color = "#34d399";
      resultBox.innerText = `Connected! Latency: ${data.connection.latency_ms}ms • Model: ${data.connection.model}`;
      checkHealth();
    } else {
      resultBox.style.background = "rgba(244, 63, 94, 0.15)";
      resultBox.style.color = "#fb7185";
      resultBox.innerText = `Connection failed: ${data.connection?.message || "Invalid Key"}`;
    }
  } catch (err) {
    resultBox.innerText = `Error: ${err.message}`;
  }
}

async function saveSettings() {
  await testApiKey();
  setTimeout(() => {
    closeSettingsModal();
  }, 1000);
}

// --- Helpers ---
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatMarkdown(text) {
  if (!text) return "";
  let html = escapeHtml(text);
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Bullet points
  html = html.replace(/^\s*[\*\-]\s+(.*)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  // Linebreaks
  html = html.replace(/\n\n/g, '<br><br>');
  html = html.replace(/\n/g, '<br>');
  return html;
}
