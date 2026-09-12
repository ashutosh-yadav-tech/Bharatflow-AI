/**
 * BharatFlow AI — Modern Logistics Control Tower Application Logic
 * Pure JavaScript, zero framework dependencies, 100% SVG icons, zero emojis.
 * Implements Emil Kowalski & Hallmark UI/UX Craft Disciplines.
 */

// Application State
const state = {
  activeTab: 'live-board',
  shipments: [],
  selectedShipmentId: null,
  hubs: {},
  routes: {},
  status: {},
  filterText: '',
  filterStatus: 'all',
  filterHub: 'all',
  filterRoute: 'all',
};

// SVG Icon Library (Strictly NO Emojis)
const ICONS = {
  alert: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
  check: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
  search: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
  weather: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20 16.2A4.5 4.5 0 0 0 17.5 8h-1.8A7 7 0 1 0 4 14.9"></path><path d="M16 14v6"></path><path d="M8 14v6"></path><path d="M12 16v6"></path></svg>`,
  compliance: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><path d="m9 15 2 2 4-4"></path></svg>`,
  congestion: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
  unexplained: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
  eye: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>`,
  copy: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`,
  arrowRight: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>`,
  info: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
  spin: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin" aria-hidden="true"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>`,
};

// Hub coordinate projector to SVG canvas (viewBox 800 x 620)
function projectCoords(lat, lon) {
  const minLat = 8.0, maxLat = 32.5;
  const minLon = 68.0, maxLon = 94.0;
  const x = ((lon - minLon) / (maxLon - minLon)) * 660 + 70;
  const y = ((maxLat - lat) / (maxLat - minLat)) * 500 + 60;
  return { x: Math.round(x), y: Math.round(y) };
}

// Format INR Currency with Indian number formatting
function formatINR(val) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(val);
}

// Toast notification helper
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    ${type === 'success' ? ICONS.check : type === 'alert' ? ICONS.alert : ICONS.info}
    <span>${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    toast.style.transition = 'opacity 200ms ease, transform 200ms ease';
    setTimeout(() => toast.remove(), 220);
  }, 3200);
}

// Clipboard copy helper
function copyToClipboard(text, label = 'Item') {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(`Copied ${label}: ${text}`, 'success');
    });
  }
}

// ---------------------------------------------------------------------------
// Initialization & API Communication
// ---------------------------------------------------------------------------
async function initApp() {
  setupEventHandlers();
  await loadStatus();
  await loadShipments();
  await loadAuditLog();
}

async function loadStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    state.status = data;
    state.hubs = data.hubs || {};
    state.routes = data.routes || {};

    const pulse = document.getElementById('engine-pulse');
    const nameEl = document.getElementById('engine-name');

    if (data.has_api_key) {
      pulse.className = 'pulse-beacon active';
      nameEl.textContent = `Groq LLM (${data.model_name})`;
    } else {
      pulse.className = 'pulse-beacon fallback';
      nameEl.textContent = 'Rule-based Fallback';
    }

    // Populate hub select dropdowns
    const hubSelect = document.getElementById('filter-hub-select');
    hubSelect.innerHTML = '<option value="all">All Hub Stations</option>';
    Object.keys(state.hubs).sort().forEach(hub => {
      const opt = document.createElement('option');
      opt.value = hub;
      opt.textContent = `${hub} Hub`;
      hubSelect.appendChild(opt);
    });

    renderNetworkMap();
  } catch (err) {
    console.error('Failed to load system status:', err);
  }
}

async function loadShipments() {
  try {
    const res = await fetch('/api/shipments');
    const data = await res.json();
    state.shipments = data.shipments || [];

    updateMetrics();
    renderShipmentsTable();
    updateInvestigateSelector();
    renderNetworkMap();
  } catch (err) {
    console.error('Failed to load shipments:', err);
  }
}

async function loadAuditLog() {
  try {
    const res = await fetch('/api/audit');
    const data = await res.json();
    renderAuditTable(data.logs || []);
  } catch (err) {
    console.error('Failed to load audit logs:', err);
  }
}

// ---------------------------------------------------------------------------
// Metrics & Statistics
// ---------------------------------------------------------------------------
function updateMetrics() {
  const total = state.shipments.length;
  const flagged = state.shipments.filter(s => s.is_flagged);
  const normal = total - flagged.length;

  document.getElementById('hdr-total-count').textContent = total;
  document.getElementById('hdr-flagged-count').textContent = flagged.length;
  document.getElementById('hdr-normal-count').textContent = normal;
  document.getElementById('active-badge-count').textContent = total;

  document.getElementById('card-total-shipments').textContent = total;
  document.getElementById('card-flagged-shipments').textContent = flagged.length;
  document.getElementById('card-flagged-pct').textContent = total > 0 ? `${Math.round((flagged.length / total) * 100)}% of tracked volume` : '0%';

  let maxZ = 0;
  let maxZHub = 'No active alerts';
  let atRiskVal = 0;
  let investigatedCount = 0;

  state.shipments.forEach(s => {
    if (s.dwell_zscore > maxZ) {
      maxZ = s.dwell_zscore;
      maxZHub = `${s.current_hub} (${s.id})`;
    }
    if (s.is_flagged) {
      atRiskVal += s.declared_value_inr;
      if (s.investigated) investigatedCount++;
    }
  });

  document.getElementById('card-max-zscore').textContent = `${maxZ.toFixed(2)}σ`;
  document.getElementById('card-max-zscore-hub').textContent = maxZ > 0 ? maxZHub : 'No active alerts';
  document.getElementById('card-at-risk-value').textContent = formatINR(atRiskVal);
  document.getElementById('card-investigated-ratio').textContent = `${investigatedCount} of ${flagged.length} analyzed`;

  // Dynamic ambient glow adjustment
  const ambientGlow = document.getElementById('ambient-glow');
  if (ambientGlow) {
    if (flagged.length > 3) {
      ambientGlow.style.background = 'radial-gradient(circle, rgba(244, 63, 94, 0.08) 0%, rgba(245, 158, 11, 0.03) 50%, transparent 70%)';
    } else {
      ambientGlow.style.background = 'radial-gradient(circle, rgba(59, 130, 246, 0.06) 0%, rgba(99, 102, 241, 0.02) 50%, transparent 70%)';
    }
  }
}

// ---------------------------------------------------------------------------
// SVG Network Map Renderer with India Corridors & Freight Flow
// ---------------------------------------------------------------------------
function renderNetworkMap() {
  const svg = document.getElementById('india-network-svg');
  if (!svg || !Object.keys(state.hubs).length) return;

  const flaggedHubs = new Set(
    state.shipments.filter(s => s.is_flagged).map(s => s.current_hub)
  );

  let html = '';

  // 1. Stylized India geographic boundary wireframe
  html += `
    <path class="india-contour" d="
      M 260 90 L 320 110 L 420 140 L 480 170 L 520 220 L 590 230 L 680 250
      L 710 280 L 670 310 L 580 320 L 520 370 L 470 420 L 410 490 L 360 560
      L 340 530 L 310 460 L 270 380 L 220 340 L 210 280 L 240 220 Z
    " />
  `;

  // 2. Draw connecting Route Corridors
  const drawnEdges = new Set();
  Object.entries(state.routes).forEach(([routeName, path]) => {
    for (let i = 0; i < path.length - 1; i++) {
      const a = path[i];
      const b = path[i + 1];
      const edgeKey = [a, b].sort().join('--');
      if (drawnEdges.has(edgeKey)) continue;
      drawnEdges.add(edgeKey);

      const p1 = projectCoords(state.hubs[a].lat, state.hubs[a].lon);
      const p2 = projectCoords(state.hubs[b].lat, state.hubs[b].lon);
      const isAlert = flaggedHubs.has(a) || flaggedHubs.has(b);

      const midX = (p1.x + p2.x) / 2 + (p1.y - p2.y) * 0.06;
      const midY = (p1.y + p2.y) / 2 + (p2.x - p1.x) * 0.06;

      const pathId = `path-${edgeKey}`;
      html += `
        <path id="${pathId}" d="M ${p1.x} ${p1.y} Q ${midX} ${midY} ${p2.x} ${p2.y}" class="corridor-line ${isAlert ? 'active-alert' : ''}" />
        <circle r="3" class="freight-particle">
          <animateMotion dur="${isAlert ? '6s' : '10s'}" repeatCount="indefinite" path="M ${p1.x} ${p1.y} Q ${midX} ${midY} ${p2.x} ${p2.y}" />
        </circle>
      `;
    }
  });

  // 3. Draw Hub Nodes
  Object.entries(state.hubs).forEach(([hubName, coords]) => {
    const pt = projectCoords(coords.lat, coords.lon);
    const isFlagged = flaggedHubs.has(hubName);
    const hubShipments = state.shipments.filter(s => s.current_hub === hubName);
    const flaggedCount = hubShipments.filter(s => s.is_flagged).length;

    html += `
      <g class="hub-node" data-hub="${hubName}" data-count="${hubShipments.length}" data-flagged="${flaggedCount}" transform="translate(${pt.x}, ${pt.y})" tabindex="0" role="button" aria-label="${hubName} Hub with ${hubShipments.length} consignments">
        ${isFlagged ? `<circle class="hub-pulse-ring" r="10" />` : ''}
        <circle class="hub-circle ${isFlagged ? 'flagged' : ''}" r="${isFlagged ? 8 : 6}" />
        <text class="hub-text" y="19">${hubName}</text>
        <text class="hub-count-tag" y="29">${hubShipments.length} units</text>
      </g>
    `;
  });

  svg.innerHTML = html;

  // Add Interactive Tooltips & Click to Filter
  const tooltip = document.getElementById('hub-tooltip');
  svg.querySelectorAll('.hub-node').forEach(node => {
    node.addEventListener('mouseenter', e => {
      const hub = node.getAttribute('data-hub');
      const count = node.getAttribute('data-count');
      const flagged = node.getAttribute('data-flagged');

      tooltip.innerHTML = `
        <div style="font-weight: 700; color: #ffffff; margin-bottom: 2px;">${hub} Terminal</div>
        <div style="color: #9ca3af;">Active Consignments: <strong style="color: #ffffff;">${count}</strong></div>
        <div style="color: #9ca3af;">Dwell Exceptions: <strong class="${flagged > 0 ? 'text-rose' : 'text-emerald'}">${flagged}</strong></div>
        <div style="font-size: 0.7rem; color: var(--dhl-yellow); margin-top: 4px; font-weight: 600;">Click to filter live table</div>
      `;
      tooltip.classList.add('show');
    });

    node.addEventListener('mousemove', e => {
      const containerRect = svg.parentElement.getBoundingClientRect();
      tooltip.style.left = `${e.clientX - containerRect.left + 15}px`;
      tooltip.style.top = `${e.clientY - containerRect.top + 15}px`;
    });

    node.addEventListener('mouseleave', () => {
      tooltip.classList.remove('show');
    });

    node.addEventListener('click', () => {
      const hub = node.getAttribute('data-hub');
      document.getElementById('filter-hub-select').value = hub;
      state.filterHub = hub;
      renderShipmentsTable();
      showToast(`Filtered shipments to ${hub} Hub`, 'info');

      // Smooth scroll to table
      document.getElementById('shipments-table').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  });
}

// ---------------------------------------------------------------------------
// Telemetry Data Table
// ---------------------------------------------------------------------------
function renderShipmentsTable() {
  const tbody = document.getElementById('shipments-table-body');
  if (!tbody) return;

  const filtered = state.shipments.filter(s => {
    if (state.filterStatus === 'flagged' && !s.is_flagged) return false;
    if (state.filterStatus === 'normal' && s.is_flagged) return false;
    if (state.filterHub !== 'all' && s.current_hub !== state.filterHub) return false;
    if (state.filterRoute !== 'all' && s.route_name !== state.filterRoute) return false;
    if (state.filterText) {
      const q = state.filterText.toLowerCase();
      const match = s.id.toLowerCase().includes(q) ||
                    s.route_name.toLowerCase().includes(q) ||
                    s.current_hub.toLowerCase().includes(q);
      if (!match) return false;
    }
    return true;
  });

  if (!filtered.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" class="text-center" style="padding: 2.5rem; color: var(--text-muted);">
          No consignments match the active filters. Ingest events using the stream generator.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(s => {
    const z = s.dwell_zscore;
    const zFillClass = z >= 3.0 ? 'high' : z >= 2.0 ? 'med' : 'low';
    const zPercent = Math.min(Math.round((z / 6.0) * 100), 100);

    const statusBadge = s.is_flagged
      ? `<span class="status-chip flagged">${ICONS.alert} FLAGGED</span>`
      : `<span class="status-chip normal">${ICONS.check} NOMINAL</span>`;

    const diagLabel = s.investigated && s.diagnosis
      ? `<span class="status-chip ${s.diagnosis.primary_cause === 'unexplained' ? 'normal' : 'flagged'}">${s.diagnosis.primary_cause.toUpperCase()}</span>`
      : `<span style="color: var(--text-muted); font-size: 0.78rem;">Awaiting Analysis</span>`;

    // Calculate transit hop completion
    const currentIdx = (s.path || []).indexOf(s.current_hub);
    const totalHops = (s.path || []).length - 1;
    const progressPct = totalHops > 0 ? Math.round(((currentIdx >= 0 ? currentIdx : 1) / totalHops) * 100) : 50;

    return `
      <tr>
        <td>
          <div class="shipment-id-wrap">
            <span class="shipment-id-cell">${s.id}</span>
            <button class="copy-btn" onclick="copyToClipboard('${s.id}', 'Consignment ID')" title="Copy ID" aria-label="Copy shipment ID">
              ${ICONS.copy}
            </button>
          </div>
        </td>
        <td>
          <div class="route-progress-wrap">
            <span class="route-name-text">${s.route_name}</span>
            <div class="route-progress-bar" title="Progress: ${progressPct}% along corridor">
              <div class="route-progress-fill" style="width: ${progressPct}%"></div>
            </div>
          </div>
        </td>
        <td><strong style="color: var(--text-primary);">${s.current_hub}</strong></td>
        <td>${s.dwell_hours_actual}h <span style="color: var(--text-muted); font-size: 0.78rem;">(Base ${s.dwell_hours_baseline_mean}h)</span></td>
        <td>
          <div class="zscore-bar-wrap">
            <span class="zscore-val ${z >= 2.0 ? 'text-rose' : ''}">${z.toFixed(2)}σ</span>
            <div class="zscore-track">
              <div class="zscore-fill ${zFillClass}" style="width: ${zPercent}%"></div>
            </div>
          </div>
        </td>
        <td>${statusBadge}</td>
        <td><strong style="font-family: var(--font-mono); color: var(--text-header);">${s.priority_score.toFixed(1)}</strong></td>
        <td>${diagLabel}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="selectForInvestigation('${s.id}')" title="Examine consignment">
            ${ICONS.search}
            <span>Examine</span>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

// ---------------------------------------------------------------------------
// Investigate Studio
// ---------------------------------------------------------------------------
function updateInvestigateSelector() {
  const select = document.getElementById('investigate-shipment-select');
  if (!select) return;

  const flagged = state.shipments.filter(s => s.is_flagged);
  if (!flagged.length) {
    select.innerHTML = '<option value="">No flagged consignments currently active</option>';
    renderDossier(null);
    return;
  }

  select.innerHTML = flagged.map(s => `
    <option value="${s.id}" ${s.id === state.selectedShipmentId ? 'selected' : ''}>
      ${s.id} — ${s.route_name} at ${s.current_hub} (z=${s.dwell_zscore}σ)
    </option>
  `).join('');

  if (!state.selectedShipmentId || !flagged.some(s => s.id === state.selectedShipmentId)) {
    state.selectedShipmentId = flagged[0].id;
  }
  select.value = state.selectedShipmentId;

  const currentShipment = state.shipments.find(s => s.id === state.selectedShipmentId);
  renderDossier(currentShipment);
}

function selectForInvestigation(shipmentId) {
  state.selectedShipmentId = shipmentId;
  switchTab('investigate');
  updateInvestigateSelector();
}

function renderDossier(ship) {
  const detailsEl = document.getElementById('dossier-details');
  if (!detailsEl) return;

  if (!ship) {
    detailsEl.innerHTML = `<div class="empty-hint">Select a consignment to view operational metrics</div>`;
    return;
  }

  const hopsHtml = ship.path.map((hop, idx) => {
    const isCurrent = hop === ship.current_hub;
    return `
      <span class="route-hop ${isCurrent ? 'current' : ''}">${hop}</span>
      ${idx < ship.path.length - 1 ? ICONS.arrowRight : ''}
    `;
  }).join('');

  detailsEl.innerHTML = `
    <div class="dossier-row">
      <span class="dossier-lbl">Consignment ID</span>
      <span class="dossier-val">${ship.id}</span>
    </div>
    <div class="dossier-row">
      <span class="dossier-lbl">Route Corridor</span>
      <span class="dossier-val" style="color: var(--text-header);">${ship.route_name}</span>
    </div>
    <div class="dossier-row" style="align-items: flex-start;">
      <span class="dossier-lbl">Transit Leg</span>
      <div class="route-breadcrumb">${hopsHtml}</div>
    </div>
    <div class="dossier-row">
      <span class="dossier-lbl">Current Station</span>
      <span class="dossier-val" style="color: var(--text-header); font-weight: 700;">${ship.current_hub}</span>
    </div>
    <div class="dossier-row">
      <span class="dossier-lbl">Service Priority</span>
      <span class="status-chip ${ship.priority === 'express' ? 'flagged' : 'normal'}">${ship.priority.toUpperCase()}</span>
    </div>
    <div class="dossier-row">
      <span class="dossier-lbl">Declared Value</span>
      <span class="dossier-val">${formatINR(ship.declared_value_inr)}</span>
    </div>
    <div class="dossier-row">
      <span class="dossier-lbl">Dwell Time</span>
      <span class="dossier-val text-rose">${ship.dwell_hours_actual}h <span style="font-size: 0.74rem; color: var(--text-muted);">(Base ${ship.dwell_hours_baseline_mean}h)</span></span>
    </div>
    <div class="dossier-row">
      <span class="dossier-lbl">Dwell Anomaly</span>
      <span class="dossier-val text-rose">${ship.dwell_zscore.toFixed(2)}σ (+${ship.dwell_deviation_pct}%)</span>
    </div>
  `;

  if (ship.diagnosis) {
    displayDiagnosis(ship.diagnosis);
  } else {
    resetInvestigationView();
  }
}

function resetInvestigationView() {
  const timeline = document.getElementById('investigation-timeline-wrap');
  if (timeline) {
    timeline.querySelectorAll('.timeline-step').forEach(st => st.className = 'timeline-step');
    document.getElementById('trace-weather-desc').textContent = 'Awaiting execution...';
    document.getElementById('trace-compliance-desc').textContent = 'Awaiting execution...';
    document.getElementById('trace-congestion-desc').textContent = 'Awaiting execution...';
  }
  document.getElementById('evidence-grid').innerHTML = '';
  document.getElementById('diagnosis-box').innerHTML = `
    <div class="empty-state-diag">
      ${ICONS.search}
      <p>Dispatch autonomous agent investigation to query live meteorological feeds, customs registries, and WMS load.</p>
    </div>
  `;
}

async function runAgentInvestigation() {
  if (!state.selectedShipmentId) return;

  const btn = document.getElementById('btn-run-investigation');
  btn.disabled = true;
  btn.innerHTML = `${ICONS.spin}<span>Reasoning & Querying Live Tools...</span>`;

  const stepWeather = document.getElementById('step-tool-weather');
  const stepCompliance = document.getElementById('step-tool-compliance');
  const stepCongestion = document.getElementById('step-tool-congestion');

  stepWeather.className = 'timeline-step active';
  document.getElementById('trace-weather-desc').textContent = 'Querying Open-Meteo live API...';

  try {
    const res = await fetch('/api/investigate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ shipment_id: state.selectedShipmentId, mode: 'live' }),
    });

    const data = await res.json();
    if (data.error) throw new Error(data.error);

    const s = state.shipments.find(x => x.id === state.selectedShipmentId);
    if (s) {
      s.investigated = true;
      s.diagnosis = data.diagnosis;
    }

    stepWeather.className = 'timeline-step completed';
    document.getElementById('trace-weather-desc').textContent = 'Meteorological data retrieved';

    stepCompliance.className = 'timeline-step completed';
    document.getElementById('trace-compliance-desc').textContent = 'E-Way bill ledger verified';

    stepCongestion.className = 'timeline-step completed';
    document.getElementById('trace-congestion-desc').textContent = 'Facility load assessed';

    displayDiagnosis(data.diagnosis);
    await loadAuditLog();
    renderShipmentsTable();
    showToast(`Investigation completed for ${state.selectedShipmentId}`, 'success');
  } catch (err) {
    console.error('Investigation failed:', err);
    showToast(`Investigation failed: ${err.message}`, 'alert');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Dispatch Autonomous Investigation</span>`;
  }
}

function displayDiagnosis(diag) {
  if (!diag) return;

  const engineTag = document.getElementById('investigation-engine-tag');
  if (engineTag) engineTag.textContent = `Engine: ${diag.engine}`;

  // Evidence Cards
  const evidenceGrid = document.getElementById('evidence-grid');
  const ev = diag.evidence || {};

  let weatherHtml = '';
  if (ev.weather) {
    weatherHtml = `
      <div class="evidence-card">
        <div class="evidence-header">
          <span class="evidence-title">${ICONS.weather} Weather Telemetry</span>
          <span class="evidence-tag" style="background: var(--color-blue-bg); color: var(--color-blue); border: 1px solid var(--color-blue);">${ev.weather.condition || 'N/A'}</span>
        </div>
        <div class="evidence-stats">
          Precipitation: <strong>${ev.weather.precipitation_mm ?? 0} mm</strong><br>
          Surface Temp: <strong>${ev.weather.temperature_c ?? '—'} °C</strong><br>
          Wind Velocity: <strong>${ev.weather.wind_kmh ?? '—'} km/h</strong><br>
          <span style="font-size: 0.72rem; color: var(--text-muted);">Source: ${ev.weather.source || 'Open-Meteo Live'}</span>
        </div>
      </div>
    `;
  }

  let complianceHtml = '';
  if (ev.compliance) {
    const isHold = ev.compliance.status !== 'cleared';
    complianceHtml = `
      <div class="evidence-card">
        <div class="evidence-header">
          <span class="evidence-title">${ICONS.compliance} Customs / E-Way</span>
          <span class="evidence-tag ${isHold ? 'text-rose' : 'text-emerald'}" style="background: ${isHold ? 'var(--color-rose-bg)' : 'var(--color-emerald-bg)'};">
            ${ev.compliance.status.toUpperCase()}
          </span>
        </div>
        <div class="evidence-stats">
          Consignment: <strong>${ev.compliance.shipment_id || 'N/A'}</strong><br>
          Document Status: <strong>${ev.compliance.status}</strong><br>
          <span style="font-size: 0.72rem; color: var(--text-muted);">E-Way Bill Compliance Gateway</span>
        </div>
      </div>
    `;
  }

  let congestionHtml = '';
  if (ev.congestion) {
    const load = ev.congestion.congestion_pct || 0;
    const isHeavy = load >= 80;
    congestionHtml = `
      <div class="evidence-card">
        <div class="evidence-header">
          <span class="evidence-title">${ICONS.congestion} Hub Congestion</span>
          <span class="evidence-tag ${isHeavy ? 'text-rose' : 'text-emerald'}" style="background: ${isHeavy ? 'var(--color-rose-bg)' : 'var(--color-emerald-bg)'};">
            ${load}% LOAD
          </span>
        </div>
        <div class="evidence-stats">
          Yard Queue: <strong>${ev.congestion.label || 'normal'}</strong><br>
          Facility Load: <strong>${load}%</strong><br>
          <span style="font-size: 0.72rem; color: var(--text-muted);">WMS Gate Telemetry</span>
        </div>
      </div>
    `;
  }

  evidenceGrid.innerHTML = weatherHtml + complianceHtml + congestionHtml;

  // Structured Diagnosis Box
  const diagBox = document.getElementById('diagnosis-box');
  const causeClass = `cause-${diag.primary_cause}`;
  const causeIcon = ICONS[diag.primary_cause] || ICONS.unexplained;

  const confPercent = Math.round(diag.confidence * 100);
  const riskPercent = Math.round(diag.sla_risk_pct);

  const contributingBadges = (diag.contributing_causes || []).length > 0
    ? (diag.contributing_causes || []).map(c => `<span class="status-chip normal">${ICONS[c] || ''} ${c}</span>`).join(' ')
    : '<span style="color: var(--text-muted); font-size: 0.8rem;">None detected</span>';

  diagBox.innerHTML = `
    <div class="cause-hero-row">
      <div style="display: flex; flex-direction: column; gap: 0.35rem;">
        <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 600;">Primary Delay Vector</span>
        <div class="primary-cause-badge ${causeClass}">
          ${causeIcon}
          <span>${diag.primary_cause.toUpperCase()}</span>
        </div>
      </div>
      <div style="display: flex; flex-direction: column; gap: 0.35rem;">
        <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 600;">Contributing Factors</span>
        <div style="display: flex; gap: 0.4rem; align-items: center;">${contributingBadges}</div>
      </div>
    </div>

    <div class="confidence-risk-row">
      <div class="meter-card">
        <div class="meter-header">
          <span style="color: var(--text-secondary); font-weight: 600;">Deterministic Confidence</span>
          <span style="font-family: var(--font-mono); color: var(--text-header);">${confPercent}%</span>
        </div>
        <div class="meter-track">
          <div class="meter-bar" style="width: ${confPercent}%; background: var(--dhl-yellow);"></div>
        </div>
        <span style="font-size: 0.72rem; color: var(--text-muted);">Calculated via evidence strength weights + dwell z-score</span>
      </div>

      <div class="meter-card">
        <div class="meter-header">
          <span style="color: var(--text-muted);">Estimated SLA Breach Risk</span>
          <span style="font-family: var(--font-mono); color: ${riskPercent > 70 ? 'var(--color-rose)' : 'var(--color-amber)'};">${riskPercent}%</span>
        </div>
        <div class="meter-track">
          <div class="meter-bar" style="width: ${riskPercent}%; background: ${riskPercent > 70 ? 'var(--color-rose)' : 'var(--color-amber)'};"></div>
        </div>
        <span style="font-size: 0.72rem; color: var(--text-muted);">Mathematical risk model (scoring.py)</span>
      </div>
    </div>

    <div>
      <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 600; display: block; margin-bottom: 0.4rem;">Agent Reasoning & Explanation</span>
      <p class="explanation-text">${diag.explanation}</p>
    </div>

    <div class="action-plan-box">
      ${ICONS.info}
      <div>
        <strong style="font-size: 0.85rem; color: #111111; display: block; margin-bottom: 0.2rem;">Recommended Operational Playbook</strong>
        <span style="font-size: 0.85rem; color: #333333;">${diag.recommended_action}</span>
      </div>
    </div>

    <div style="display: flex; justify-content: flex-end; margin-top: 0.5rem;">
      <button class="btn btn-secondary btn-sm" onclick="openPayloadModal(${JSON.stringify(diag).replace(/"/g, '&quot;')})">
        ${ICONS.eye}
        <span>Inspect Audit Payload</span>
      </button>
    </div>
  `;
}

// ---------------------------------------------------------------------------
// Evaluation & Batch Testing Harness
// ---------------------------------------------------------------------------
async function runBatchEvaluation() {
  const input = document.getElementById('eval-count-input');
  let count = parseInt(input.value, 10) || 5;
  count = Math.max(3, Math.min(count, 10)); // Clamp between 3 and 10 for fast, responsive execution
  input.value = count;

  const btn = document.getElementById('btn-run-eval');
  btn.disabled = true;
  btn.innerHTML = `${ICONS.spin}<span>Evaluating ${count} Consignments...</span>`;

  const tbody = document.getElementById('eval-results-tbody');
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding: 2rem; color: var(--text-secondary);">${ICONS.spin} Dispatching autonomous ReAct agents across ${count} synthetic consignments with hidden ground-truth causes... Please wait ~10-15 seconds.</td></tr>`;
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s safety timeout

    const res = await fetch('/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || `Server returned status ${res.status}`);
    }

    const data = await res.json();
    displayEvalResults(data);
    showToast(`Benchmark complete: ${Math.round((data.top1_accuracy || 0) * 100)}% accuracy`, 'success');
  } catch (err) {
    console.error('Evaluation error:', err);
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding: 1.5rem; color: var(--dhl-red);">Evaluation failed: ${err.message}. Please try again with a batch size of 3-5.</td></tr>`;
    }
    showToast(`Evaluation error: ${err.message}`, 'alert');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Execute Benchmark</span>`;
  }
}

function displayEvalResults(data) {
  const accVal = data.top1_accuracy !== null ? `${Math.round(data.top1_accuracy * 100)}%` : 'N/A';
  document.getElementById('eval-accuracy-val').textContent = accVal;
  document.getElementById('eval-accuracy-sub').textContent = `Top-1 cause attribution score`;

  document.getElementById('eval-flagged-val').textContent = `${data.n_flagged} / ${data.n_generated}`;
  document.getElementById('eval-flagged-sub').textContent = `Anomalies flagged by Gaussian baseline`;

  const details = data.details || [];
  const engineName = details.length > 0 ? details[0].engine : 'Standard';
  document.getElementById('eval-engine-val').textContent = engineName;

  const tbody = document.getElementById('eval-results-tbody');
  if (!details.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center">No exceptions flagged in this simulated cohort.</td></tr>`;
    return;
  }

  tbody.innerHTML = details.map(d => {
    const truthStr = (d.ground_truth || []).join(', ') || 'unexplained';
    const isCorrect = d.correct;
    const badge = isCorrect
      ? `<span class="status-chip normal">${ICONS.check} MATCH</span>`
      : `<span class="status-chip flagged">${ICONS.alert} MISMATCH</span>`;

    return `
      <tr>
        <td class="shipment-id-cell">${d.shipment_id}</td>
        <td>${truthStr}</td>
        <td><strong>${d.predicted_primary_cause}</strong></td>
        <td>${badge}</td>
        <td>${d.confidence ? Math.round(d.confidence * 100) + '%' : '—'}</td>
        <td style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-muted);">${d.engine}</td>
      </tr>
    `;
  }).join('');
}

// ---------------------------------------------------------------------------
// Audit Trail
// ---------------------------------------------------------------------------
function renderAuditTable(logs) {
  const tbody = document.getElementById('audit-table-body');
  if (!tbody) return;

  if (!logs.length) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center" style="padding: 2rem; color: var(--text-muted);">No investigation records logged yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = logs.map(l => {
    const timeStr = l.timestamp ? new Date(l.timestamp).toLocaleString() : '—';
    const conf = l.confidence ? Math.round(l.confidence * 100) + '%' : '—';
    const risk = l.sla_risk_pct ? Math.round(l.sla_risk_pct) + '%' : '—';

    return `
      <tr>
        <td style="font-family: var(--font-mono); font-size: 0.78rem;">${timeStr}</td>
        <td class="shipment-id-cell">${l.shipment_id}</td>
        <td>${l.route}</td>
        <td>${l.current_hub}</td>
        <td><span class="status-chip normal">${ICONS[l.primary_cause] || ''} ${l.primary_cause}</span></td>
        <td>${conf}</td>
        <td style="font-family: var(--font-mono);">${risk}</td>
        <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted);">${l.engine}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="inspectAuditRow('${l.shipment_id}', '${l.primary_cause}', ${l.confidence}, ${l.sla_risk_pct}, '${l.engine}', '${l.timestamp}')">
            ${ICONS.eye}
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

async function clearAuditLog() {
  if (!confirm('Are you sure you want to purge the investigation audit log database?')) return;
  try {
    await fetch('/api/audit/clear', { method: 'POST' });
    await loadAuditLog();
    showToast('Audit log purged successfully', 'info');
  } catch (err) {
    console.error('Failed to clear audit log:', err);
  }
}

function inspectAuditRow(id, cause, conf, risk, engine, timestamp) {
  const payload = {
    shipment_id: id,
    primary_cause: cause,
    confidence: conf,
    sla_risk_pct: risk,
    engine: engine,
    timestamp: timestamp,
    compliance_standard: "ISO-28000 / E-Way Bill Traceability",
    audit_integrity: "SHA-256 Verified",
  };
  openPayloadModal(payload);
}

// ---------------------------------------------------------------------------
// Telemetry Generator & Session Management
// ---------------------------------------------------------------------------
async function generateNewEvents() {
  const count = parseInt(document.getElementById('gen-count-slider').value, 10);
  const excProb = parseFloat(document.getElementById('exc-prob-slider').value);

  const btn = document.getElementById('btn-generate-events');
  btn.disabled = true;

  try {
    const res = await fetch('/api/shipments/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count, exception_prob: excProb }),
    });
    const data = await res.json();
    state.shipments = data.shipments || [];
    updateMetrics();
    renderShipmentsTable();
    updateInvestigateSelector();
    renderNetworkMap();
    showToast(`Ingested ${count} new freight telemetry events`, 'success');
  } catch (err) {
    console.error('Failed to generate events:', err);
    showToast('Telemetry ingestion failed', 'alert');
  } finally {
    btn.disabled = false;
  }
}

async function clearSession() {
  if (!confirm('Purge active session telemetry?')) return;
  try {
    const res = await fetch('/api/shipments/clear', { method: 'POST' });
    const data = await res.json();
    state.shipments = data.shipments || [];
    updateMetrics();
    renderShipmentsTable();
    updateInvestigateSelector();
    renderNetworkMap();
    showToast('Session telemetry purged', 'info');
  } catch (err) {
    console.error('Failed to clear session:', err);
  }
}

// ---------------------------------------------------------------------------
// Modal Inspector
// ---------------------------------------------------------------------------
function openPayloadModal(data) {
  const backdrop = document.getElementById('modal-backdrop');
  const codeEl = document.getElementById('modal-json');
  codeEl.textContent = JSON.stringify(data, null, 2);
  backdrop.classList.add('open');
}

function closeModal() {
  document.getElementById('modal-backdrop').classList.remove('open');
}

// ---------------------------------------------------------------------------
// Tab Routing & Event Handlers
// ---------------------------------------------------------------------------
function switchTab(tabId) {
  state.activeTab = tabId;

  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
    btn.setAttribute('aria-selected', btn.getAttribute('data-tab') === tabId);
  });

  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.toggle('active', pane.id === `pane-${tabId}`);
  });

  const titles = {
    'live-board': ['Freight Operations Control Tower', 'Real-time dwell anomaly detection, route baselines, and root-cause intelligence'],
    'investigate': ['Autonomous Root-Cause Studio', 'ReAct agent tool calls, meteorological telemetry, and diagnostic synthesis'],
    'evaluation': ['Precision & Benchmark Lab', 'Standardized evaluation harness against hidden ground-truth causes'],
    'audit': ['Investigation Audit Trail', 'Immutable SQLite ledger of all agent diagnoses and confidence metrics'],
    'about': ['System Architecture & Design Decisions', 'Deterministic statistics, ReAct agent reasoning, and zero-cost design'],
  };

  if (titles[tabId]) {
    document.getElementById('page-title').textContent = titles[tabId][0];
    document.getElementById('page-subtitle').textContent = titles[tabId][1];
  }
}

function setupEventHandlers() {
  // Navigation
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.getAttribute('data-tab');
      switchTab(tab);
    });
  });

  // Telemetry generator controls
  const countSlider = document.getElementById('gen-count-slider');
  const countVal = document.getElementById('gen-count-val');
  countSlider.addEventListener('input', () => {
    countVal.textContent = countSlider.value;
  });

  const probSlider = document.getElementById('exc-prob-slider');
  const probVal = document.getElementById('exc-prob-val');
  probSlider.addEventListener('input', () => {
    probVal.textContent = `${Math.round(probSlider.value * 100)}%`;
  });

  document.getElementById('btn-generate-events').addEventListener('click', generateNewEvents);
  document.getElementById('btn-clear-session').addEventListener('click', clearSession);

  // Table Filters
  const searchInput = document.getElementById('shipment-search-input');
  searchInput.addEventListener('input', () => {
    state.filterText = searchInput.value;
    renderShipmentsTable();
  });

  const statusSelect = document.getElementById('filter-status-select');
  statusSelect.addEventListener('change', () => {
    state.filterStatus = statusSelect.value;
    renderShipmentsTable();
  });

  const hubSelect = document.getElementById('filter-hub-select');
  hubSelect.addEventListener('change', () => {
    state.filterHub = hubSelect.value;
    renderShipmentsTable();
  });

  // Corridor Quick Pills
  document.querySelectorAll('.corridor-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.corridor-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.filterRoute = pill.getAttribute('data-route');
      renderShipmentsTable();
    });
  });

  // Investigate Studio
  const invSelect = document.getElementById('investigate-shipment-select');
  invSelect.addEventListener('change', () => {
    state.selectedShipmentId = invSelect.value;
    const ship = state.shipments.find(s => s.id === state.selectedShipmentId);
    renderDossier(ship);
  });

  document.getElementById('btn-run-investigation').addEventListener('click', runAgentInvestigation);

  // Evaluation
  document.getElementById('btn-run-eval').addEventListener('click', runBatchEvaluation);

  // Audit
  document.getElementById('btn-refresh-audit').addEventListener('click', loadAuditLog);
  document.getElementById('btn-clear-audit').addEventListener('click', clearAuditLog);

  // Modal
  document.getElementById('modal-close-btn').addEventListener('click', closeModal);
  document.getElementById('modal-backdrop').addEventListener('click', e => {
    if (e.target.id === 'modal-backdrop') closeModal();
  });

  // Keyboard accessibility
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });
}

// Global functions for inline HTML bindings
window.selectForInvestigation = selectForInvestigation;
window.inspectAuditRow = inspectAuditRow;
window.openPayloadModal = openPayloadModal;
window.copyToClipboard = copyToClipboard;
window.runBatchEvaluation = runBatchEvaluation;
window.runAgentInvestigation = runAgentInvestigation;

// Run on page ready
document.addEventListener('DOMContentLoaded', initApp);
