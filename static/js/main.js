// CXO Finder — main.js

const TITLE_COLORS = {
  'CEO': '#ef4444',
  'Chief Executive Officer': '#ef4444',
  'CFO': '#8b5cf6',
  'Chief Financial Officer': '#8b5cf6',
  'CTO': '#06b6d4',
  'Chief Technology Officer': '#06b6d4',
  'COO': '#f59e0b',
  'Chief Operating Officer': '#f59e0b',
  'CMO': '#ec4899',
  'Chief Marketing Officer': '#ec4899',
  'CIO': '#10b981',
  'Chief Information Officer': '#10b981',
  'CISO': '#f97316',
  'CPO': '#a78bfa',
  'President': '#ef4444',
  'Chairman': '#94a3b8',
  'Chairwoman': '#94a3b8',
};

function getTitleColor(title) {
  if (!title) return '#3b82f6';
  for (const [key, color] of Object.entries(TITLE_COLORS)) {
    if (title.toUpperCase().includes(key.toUpperCase())) return color;
  }
  return '#3b82f6';
}

function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
}

function getShortTitle(title) {
  const map = {
    'Chief Executive Officer': 'CEO',
    'Chief Financial Officer': 'CFO',
    'Chief Technology Officer': 'CTO',
    'Chief Operating Officer': 'COO',
    'Chief Marketing Officer': 'CMO',
    'Chief Information Officer': 'CIO',
    'Chief Information Security Officer': 'CISO',
    'Chief Product Officer': 'CPO',
    'Chief Data Officer': 'CDO',
    'Chief Human Resources Officer': 'CHRO',
  };
  return map[title] || title;
}

function renderCard(person) {
  const color = getTitleColor(person.title || '');
  const initials = getInitials(person.name);
  const shortTitle = getShortTitle(person.title || 'Executive');
  const source = person.source || 'database';

  const linkedinUrl = person.linkedin || 
    `https://linkedin.com/search/results/people/?keywords=${encodeURIComponent(person.name + ' ' + person.company)}`;
  
  const emailHtml = person.email
    ? `<a href="mailto:${person.email}" class="card-btn">✉ Email</a>`
    : `<a href="${linkedinUrl}" target="_blank" class="card-btn">🔗 LinkedIn</a>`;

  return `
    <div class="cxo-card" style="--title-color: ${color}">
      <span class="source-badge source-${source}">${source === 'database' ? '✓ DB' : '🌐 Web'}</span>
      <div class="card-avatar">${initials}</div>
      <div class="card-name">${person.name}</div>
      <div class="card-title-badge">${shortTitle}</div>
      <div class="card-company">🏢 ${person.company || 'N/A'}</div>
      <div class="card-actions">
        <a href="${linkedinUrl}" target="_blank" class="card-btn">🔗 LinkedIn</a>
        <button class="card-btn" onclick="copyName('${person.name}')">📋 Copy</button>
      </div>
    </div>`;
}

function copyName(name) {
  navigator.clipboard.writeText(name).then(() => {
    showToast(`Copied: ${name}`);
  });
}

function showToast(msg) {
  const t = document.createElement('div');
  t.style.cssText = `
    position:fixed; bottom:1.5rem; right:1.5rem; z-index:9999;
    background:#1e293b; border:1px solid #3b82f6; border-radius:10px;
    color:#e2e8f0; padding:0.75rem 1.25rem; font-size:0.875rem;
    box-shadow:0 4px 20px rgba(0,0,0,0.4);
    animation: slideIn 0.3s ease;
  `;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2500);
}

async function doSearch() {
  const input = document.getElementById('companyInput');
  const company = input.value.trim();
  
  if (!company) {
    input.focus();
    showToast('Please enter a company name');
    return;
  }

  const resultsSection = document.getElementById('resultsSection');
  const btn = document.getElementById('searchBtn');
  
  resultsSection.innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <p style="color:var(--muted)">Searching for CXO contacts at <strong style="color:var(--text)">${company}</strong>...</p>
    </div>`;

  btn.disabled = true;
  btn.innerHTML = '⏳ Searching...';

  try {
    const resp = await fetch('/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company })
    });

    const data = await resp.json();
    
    if (data.error) {
      resultsSection.innerHTML = `<div class="error-msg">⚠️ ${data.error}</div>`;
      return;
    }

    if (!data.results || data.results.length === 0) {
      resultsSection.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <div class="empty-title">No CXO contacts found</div>
          <p>Try a different company name or check the spelling.</p>
          <p style="margin-top:0.5rem;font-size:0.8rem">Examples: Microsoft, Apple, Google, Amazon</p>
        </div>`;
      return;
    }

    // Stats
    const dbCount = data.results.filter(r => r.source === 'database').length;
    const webCount = data.results.filter(r => r.source === 'web').length;

    resultsSection.innerHTML = `
      <div class="results-header">
        <div class="results-title">Results for "<strong>${data.company}</strong>"</div>
        <div class="results-count">${data.count} found</div>
      </div>
      <div style="display:flex;gap:0.5rem;margin-bottom:1rem;flex-wrap:wrap">
        ${dbCount ? `<span style="font-size:0.8rem;padding:0.25rem 0.75rem;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);border-radius:20px;color:#10b981">✓ ${dbCount} from database</span>` : ''}
        ${webCount ? `<span style="font-size:0.8rem;padding:0.25rem 0.75rem;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);border-radius:20px;color:#f59e0b">🌐 ${webCount} from web</span>` : ''}
      </div>
      <div class="results-grid">
        ${data.results.map(renderCard).join('')}
      </div>`;

  } catch (err) {
    resultsSection.innerHTML = `<div class="error-msg">❌ Search failed: ${err.message}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🔍 Search';
  }
}

function quickSearch(company) {
  document.getElementById('companyInput').value = company;
  doSearch();
}

// Enter key
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('companyInput');
  if (input) {
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') doSearch();
    });
  }
});
