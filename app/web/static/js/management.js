const el = {
  boothsList: document.getElementById('boothsList'),
  boothNameInput: document.getElementById('boothNameInput'),
  createBoothBtn: document.getElementById('createBoothBtn'),
  createStatus: document.getElementById('createStatus'),
};

function escapeHtml(v) {
  return String(v ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
}

function setStatus(text, type = '') {
  el.createStatus.textContent = text;
  el.createStatus.className = 'mgmt-status' + (type ? ` ${type}` : '');
}

async function apiJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try { const d = await response.json(); message = d.detail || d.message || message; } catch (_) {}
    throw new Error(message);
  }
  return response.json();
}

function renderBooths(booths) {
  if (!booths.length) {
    el.boothsList.innerHTML = '<div class="booths-empty">Нет стендов. Добавьте первый стенд выше.</div>';
    return;
  }
  el.boothsList.innerHTML = booths.map(b => `
    <div class="booth-row" data-id="${b.id}">
      <span class="booth-id">#${escapeHtml(b.id)}</span>
      <span class="booth-name">${escapeHtml(b.name)}</span>
      <span class="booth-meta">Создан: ${escapeHtml(formatDate(b.created_at))}</span>
      <div class="booth-actions">
        <a href="/booth/${escapeHtml(b.id)}" class="mgmt-btn mgmt-btn-open" target="_blank">Открыть</a>
        <button class="mgmt-btn mgmt-btn-danger" data-id="${b.id}">Удалить</button>
      </div>
    </div>
  `).join('');

  el.boothsList.querySelectorAll('[data-id]').forEach(btn => {
    if (btn.tagName === 'BUTTON') {
      btn.addEventListener('click', () => deleteBooth(Number(btn.dataset.id)));
    }
  });
}

async function loadBooths() {
  try {
    const data = await apiJson('/api/booths');
    renderBooths(data.booths || []);
  } catch (err) {
    el.boothsList.innerHTML = `<div class="booths-empty">Ошибка загрузки: ${escapeHtml(err.message)}</div>`;
  }
}

async function createBooth() {
  const name = el.boothNameInput.value.trim();
  if (!name) {
    setStatus('Введите название стенда', 'error');
    el.boothNameInput.focus();
    return;
  }
  el.createBoothBtn.disabled = true;
  setStatus('Создание…');
  try {
    const data = await apiJson('/api/booths', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
    el.boothNameInput.value = '';
    setStatus(`Стенд «${data.booth.name}» создан (#${data.booth.id})`, 'ok');
    await loadBooths();
  } catch (err) {
    setStatus(`Ошибка: ${err.message}`, 'error');
  } finally {
    el.createBoothBtn.disabled = false;
  }
}

async function deleteBooth(id) {
  if (!confirm(`Удалить стенд #${id}? Это действие необратимо.`)) return;
  try {
    await apiJson(`/api/booths/${id}`, { method: 'DELETE' });
    await loadBooths();
    setStatus(`Стенд #${id} удалён`);
  } catch (err) {
    setStatus(`Ошибка удаления: ${err.message}`, 'error');
  }
}

el.createBoothBtn.addEventListener('click', createBooth);
el.boothNameInput.addEventListener('keydown', e => { if (e.key === 'Enter') createBooth(); });

loadBooths();
