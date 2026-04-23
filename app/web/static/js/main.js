const state = {
  config: null,
  metadata: null,
  parkingTimer: null,
  carouselTimer: null,
  carouselGeneration: 0,
  modeCheckTimer: null,
  carouselIndex: 0,
  carouselItems: [],
  dirty: false,
  settingsOpen: false,
};

const el = {
  placesList: document.getElementById('placesList'),
  hoursList: document.getElementById('hoursList'),
  tariffsList: document.getElementById('tariffsList'),
  hoursPanel: document.getElementById('hoursPanel'),
  placesPanel: document.getElementById('placesPanel'),
  tariffsPanel: document.getElementById('tariffsPanel'),
  closedPanel: document.getElementById('closedPanel'),
  closedMessageText: document.getElementById('closedMessageText'),
  carouselPanel: document.getElementById('carouselPanel'),
  carouselStage: document.getElementById('carouselStage'),
  carouselEmpty: document.getElementById('carouselEmpty'),
  settingsHotspot: document.getElementById('settingsHotspot'),
  settingsBackdrop: document.getElementById('settingsBackdrop'),
  settingsClose: document.getElementById('settingsClose'),
  settingsMetaLine: document.getElementById('settingsMetaLine'),
  settingsStatus: document.getElementById('settingsStatus'),
  saveSettingsButton: document.getElementById('saveSettingsButton'),
  cancelSettingsButton: document.getElementById('cancelSettingsButton'),
  reloadDiskButton: document.getElementById('reloadDiskButton'),
  testParserButton: document.getElementById('testParserButton'),
  configPathPreview: document.getElementById('configPathPreview'),
  loadedAtPreview: document.getElementById('loadedAtPreview'),
  savedAtPreview: document.getElementById('savedAtPreview'),
  rawYamlOutput: document.getElementById('rawYamlOutput'),
  parserTestOutput: document.getElementById('parserTestOutput'),
  mediaFilesList: document.getElementById('mediaFilesList'),
  mediaFileInput: document.getElementById('mediaFileInput'),
  uploadMediaButton: document.getElementById('uploadMediaButton'),
};

const fields = {
  timezoneInput: document.getElementById('timezoneInput'),
  localeInput: document.getElementById('localeInput'),
  clockFormatInput: document.getElementById('clockFormatInput'),
  showClockInput: document.getElementById('showClockInput'),
  parserServerInput: document.getElementById('parserServerInput'),
  parserPathInput: document.getElementById('parserPathInput'),
  parserTokenInput: document.getElementById('parserTokenInput'),
  workingHoursInput: document.getElementById('workingHoursInput'),
  tariffsInput: document.getElementById('tariffsInput'),
  adsPathInput: document.getElementById('adsPathInput'),
  carouselSecondsInput: document.getElementById('carouselSecondsInput'),
  freePlacesColorInput: document.getElementById('freePlacesColorInput'),
  noPlacesColorInput: document.getElementById('noPlacesColorInput'),
  noDataColorInput: document.getElementById('noDataColorInput'),
  hoursTextColorInput: document.getElementById('hoursTextColorInput'),
  tariffsTextColorInput: document.getElementById('tariffsTextColorInput'),
  closedMessageColorInput: document.getElementById('closedMessageColorInput'),
  panelBackgroundColorInput: document.getElementById('panelBackgroundColorInput'),
  cardBackgroundColorInput: document.getElementById('cardBackgroundColorInput'),
  borderColorInput: document.getElementById('borderColorInput'),
  primaryTextColorInput: document.getElementById('primaryTextColorInput'),
  secondaryTextColorInput: document.getElementById('secondaryTextColorInput'),
  backgroundStartInput: document.getElementById('backgroundStartInput'),
  backgroundEndInput: document.getElementById('backgroundEndInput'),
  manualModeInput: document.getElementById('manualModeInput'),
  scheduleEnabledInput: document.getElementById('scheduleEnabledInput'),
  scheduleFromInput: document.getElementById('scheduleFromInput'),
  scheduleToInput: document.getElementById('scheduleToInput'),
  closedTextInput: document.getElementById('closedTextInput'),
  showHoursBlockInput: document.getElementById('showHoursBlockInput'),
  showPlacesBlockInput: document.getElementById('showPlacesBlockInput'),
  showTariffsBlockInput: document.getElementById('showTariffsBlockInput'),
  showCarouselBlockInput: document.getElementById('showCarouselBlockInput'),
};

const tabButtons = Array.from(document.querySelectorAll('.tab-btn'));
const tabPanels = Array.from(document.querySelectorAll('.tab-panel'));

function escapeHtml(v) {
  return String(v ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' Б';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' КБ';
  return (bytes / 1048576).toFixed(1) + ' МБ';
}

function toLines(text) {
  return String(text || '').split('\n').map(i => i.trim()).filter(Boolean);
}

function parseColorToHex(value) {
  const raw = String(value || '').trim();
  const hex = raw.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
  if (hex) {
    let h = hex[1];
    if (h.length === 3) h = h.split('').map(ch => ch + ch).join('');
    return `#${h.toLowerCase()}`;
  }
  const rgba = raw.match(/^rgba?\(([^)]+)\)$/i);
  if (!rgba) return '#000000';
  const parts = rgba[1].split(',').map(p => p.trim());
  if (parts.length < 3) return '#000000';
  const rgb = parts.slice(0, 3).map(v => Math.max(0, Math.min(255, Number(v) || 0)));
  return `#${rgb.map(v => Math.round(v).toString(16).padStart(2, '0')).join('')}`;
}

function hexToRgba(value) {
  const hex = parseColorToHex(value).replace('#', '');
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, 1)`;
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try { const data = await response.json(); message = data.detail || data.message || message; } catch (_) {}
    throw new Error(message);
  }
  return response.json();
}

function renderStack(container, items) {
  if (!Array.isArray(items) || !items.length) {
    container.innerHTML = '<div class="stack-item"><span>Нет данных</span></div>';
    return;
  }
  container.innerHTML = items.map(item =>
    `<div class="stack-item"><span>${escapeHtml(item)}</span></div>`
  ).join('');
}

function placeClass(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'danger';
  if (Number(value) === 0) return 'warn';
  return 'ok';
}

function renderPlaces(data) {
  const levels = Array.isArray(data?.levels) ? data.levels : [];
  if (!levels.length) {
    el.placesList.innerHTML = '<div class="place-card"><div class="place-name">Нет данных</div><div class="place-value danger">--</div></div>';
    return;
  }
  el.placesList.innerHTML = levels.map(item => {
    const value = (item.free === null || item.free === undefined) ? '--' : item.free;
    return `<article class="place-card"><div class="place-name">${escapeHtml(item.label || 'Уровень')}</div><div class="place-value ${placeClass(item.free)}">${escapeHtml(value)}</div></article>`;
  }).join('');
}

function getEffectiveMode(config) {
  const om = config.operating_mode;
  if (!om) return 'normal';
  if (om.schedule_enabled) {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    const current = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
    const from = om.schedule_from || '08:00';
    const to = om.schedule_to || '22:00';
    return (current >= from && current < to) ? 'normal' : 'closed';
  }
  return om.manual_mode || 'normal';
}

function applyDisplayMode(config) {
  const isClosed = getEffectiveMode(config) === 'closed';
  const b = config.ui?.blocks || {};
  el.hoursPanel.style.display = (b.show_working_hours ?? true) ? '' : 'none';
  el.placesPanel.style.display = (!isClosed && (b.show_free_spaces ?? true)) ? '' : 'none';
  el.tariffsPanel.style.display = (!isClosed && (b.show_tariffs ?? true)) ? '' : 'none';
  el.closedPanel.style.display = isClosed ? '' : 'none';
  el.closedMessageText.textContent = config.operating_mode?.closed_text || 'Parking is closed';
  el.carouselPanel.style.display = (b.show_carousel ?? true) ? '' : 'none';
}

function applyAppearance(config) {
  const a = config.appearance;
  document.documentElement.style.setProperty('--good', a.free_places_color);
  document.documentElement.style.setProperty('--warn', a.no_places_color);
  document.documentElement.style.setProperty('--danger', a.no_data_color);
  document.documentElement.style.setProperty('--hours-text', a.hours_text_color);
  document.documentElement.style.setProperty('--tariffs-text', a.tariffs_text_color);
  document.documentElement.style.setProperty('--panel', a.panel_background_color);
  document.documentElement.style.setProperty('--panel-soft', a.card_background_color);
  document.documentElement.style.setProperty('--line', a.border_color);
  document.documentElement.style.setProperty('--text', a.primary_text_color);
  document.documentElement.style.setProperty('--muted', a.secondary_text_color);
  document.documentElement.style.setProperty('--bg-start', a.background_start);
  document.documentElement.style.setProperty('--bg-end', a.background_end);
  document.documentElement.style.setProperty('--closed-color', a.closed_message_color);
}

function renderConfig(config) {
  el.settingsHotspot.style.display = config.ui.settings_access.hidden_hotspot_enabled ? 'block' : 'none';
  renderStack(el.hoursList, config.content.working_hours);
  renderStack(el.tariffsList, config.content.tariffs);
  applyAppearance(config);
  applyDisplayMode(config);
}

function fillForm(config, metadata) {
  fields.timezoneInput.value = config.app.timezone;
  fields.localeInput.value = config.app.locale;
  fields.clockFormatInput.value = config.app.clock_format ?? 'HH:mm';
  fields.showClockInput.value = String(config.app.show_clock ?? true);
  fields.parserServerInput.value = config.parking.parser.server;
  fields.parserPathInput.value = config.parking.parser.path;
  fields.parserTokenInput.value = config.parking.parser.token;
  fields.workingHoursInput.value = config.content.working_hours.join('\n');
  fields.tariffsInput.value = config.content.tariffs.join('\n');
  fields.adsPathInput.value = config.media.ads_path;
  fields.carouselSecondsInput.value = config.media.carousel_seconds;
  fields.freePlacesColorInput.value = parseColorToHex(config.appearance.free_places_color);
  fields.noPlacesColorInput.value = parseColorToHex(config.appearance.no_places_color);
  fields.noDataColorInput.value = parseColorToHex(config.appearance.no_data_color);
  fields.hoursTextColorInput.value = parseColorToHex(config.appearance.hours_text_color);
  fields.tariffsTextColorInput.value = parseColorToHex(config.appearance.tariffs_text_color);
  fields.closedMessageColorInput.value = parseColorToHex(config.appearance.closed_message_color);
  fields.panelBackgroundColorInput.value = parseColorToHex(config.appearance.panel_background_color);
  fields.cardBackgroundColorInput.value = parseColorToHex(config.appearance.card_background_color);
  fields.borderColorInput.value = parseColorToHex(config.appearance.border_color);
  fields.primaryTextColorInput.value = parseColorToHex(config.appearance.primary_text_color);
  fields.secondaryTextColorInput.value = parseColorToHex(config.appearance.secondary_text_color);
  fields.backgroundStartInput.value = parseColorToHex(config.appearance.background_start);
  fields.backgroundEndInput.value = parseColorToHex(config.appearance.background_end);
  const b = config.ui?.blocks || {};
  fields.showHoursBlockInput.checked = b.show_working_hours ?? true;
  fields.showPlacesBlockInput.checked = b.show_free_spaces ?? true;
  fields.showTariffsBlockInput.checked = b.show_tariffs ?? true;
  fields.showCarouselBlockInput.checked = b.show_carousel ?? true;
  const om = config.operating_mode || {};
  fields.manualModeInput.value = om.manual_mode || 'normal';
  fields.scheduleEnabledInput.checked = om.schedule_enabled ?? false;
  fields.scheduleFromInput.value = om.schedule_from || '08:00';
  fields.scheduleToInput.value = om.schedule_to || '22:00';
  fields.closedTextInput.value = om.closed_text || 'Parking is closed';
  el.configPathPreview.textContent = metadata?.config_path || '—';
  el.loadedAtPreview.textContent = metadata?.loaded_at || '—';
  el.savedAtPreview.textContent = metadata?.saved_at || '—';
  el.settingsMetaLine.textContent = metadata?.config_path ? `Файл: ${metadata.config_path}` : 'Файл конфигурации не найден';
  state.dirty = false;
  updateDirtyState();
}

function readForm() {
  return {
    version: 1,
    app: {
      timezone: fields.timezoneInput.value.trim() || 'Europe/Moscow',
      locale: fields.localeInput.value.trim() || 'ru-RU',
      clock_format: fields.clockFormatInput.value.trim() || 'HH:mm',
      show_clock: fields.showClockInput.value === 'true',
    },
    parking: {
      parser: {
        server: fields.parserServerInput.value.trim(),
        path: fields.parserPathInput.value.trim(),
        token: fields.parserTokenInput.value.trim(),
      },
    },
    content: {
      working_hours: toLines(fields.workingHoursInput.value),
      tariffs: toLines(fields.tariffsInput.value),
    },
    media: {
      ads_path: fields.adsPathInput.value.trim() || '/data/ads',
      carousel_seconds: Number(fields.carouselSecondsInput.value || 8),
      allowed_extensions: state.config.media.allowed_extensions,
    },
    ui: {
      settings_access: state.config.ui.settings_access,
      diagnostics: state.config.ui.diagnostics,
      blocks: {
        show_working_hours: fields.showHoursBlockInput.checked,
        show_free_spaces: fields.showPlacesBlockInput.checked,
        show_tariffs: fields.showTariffsBlockInput.checked,
        show_carousel: fields.showCarouselBlockInput.checked,
      },
    },
    operating_mode: {
      manual_mode: fields.manualModeInput.value,
      schedule_enabled: fields.scheduleEnabledInput.checked,
      schedule_from: fields.scheduleFromInput.value || '08:00',
      schedule_to: fields.scheduleToInput.value || '22:00',
      closed_text: fields.closedTextInput.value.trim() || 'Parking is closed',
    },
    appearance: {
      free_places_color: hexToRgba(fields.freePlacesColorInput.value),
      no_places_color: hexToRgba(fields.noPlacesColorInput.value),
      no_data_color: hexToRgba(fields.noDataColorInput.value),
      hours_text_color: hexToRgba(fields.hoursTextColorInput.value),
      tariffs_text_color: hexToRgba(fields.tariffsTextColorInput.value),
      closed_message_color: hexToRgba(fields.closedMessageColorInput.value),
      panel_background_color: hexToRgba(fields.panelBackgroundColorInput.value),
      card_background_color: hexToRgba(fields.cardBackgroundColorInput.value),
      border_color: hexToRgba(fields.borderColorInput.value),
      primary_text_color: hexToRgba(fields.primaryTextColorInput.value),
      secondary_text_color: hexToRgba(fields.secondaryTextColorInput.value),
      background_start: hexToRgba(fields.backgroundStartInput.value),
      background_end: hexToRgba(fields.backgroundEndInput.value),
    },
  };
}

function updateDirtyState() {
  el.saveSettingsButton.disabled = !state.dirty;
  el.settingsStatus.textContent = state.dirty ? 'Есть несохранённые изменения' : 'Настройки синхронизированы с файлом';
}

function markDirty() { state.dirty = true; updateDirtyState(); }

async function loadSettings() {
  const data = await api('/api/settings');
  state.config = data.config;
  state.metadata = data.metadata;
  renderConfig(state.config);
  fillForm(state.config, state.metadata);
  return data;
}

async function loadRawYaml() {
  const data = await api('/api/settings/raw');
  el.rawYamlOutput.textContent = data.raw_yaml || 'Пустой YAML';
}

function clearCarousel() {
  state.carouselGeneration++;
  if (state.carouselTimer) { window.clearTimeout(state.carouselTimer); state.carouselTimer = null; }
  state.carouselItems = [];
  state.carouselIndex = 0;
  Array.from(el.carouselStage.querySelectorAll('.carousel-item')).forEach(node => node.remove());
}

function activateCarouselItem(index) {
  const nodes = Array.from(el.carouselStage.querySelectorAll('.carousel-item'));
  nodes.forEach((node, i) => {
    const active = i === index;
    node.classList.toggle('active', active);
    const video = node.querySelector('video');
    if (!video) return;
    if (active) { video.currentTime = 0; const p = video.play(); if (p?.catch) p.catch(() => {}); }
    else { video.pause(); }
  });
}

function scheduleNextSlide() {
  const gen = state.carouselGeneration;
  const nodes = Array.from(el.carouselStage.querySelectorAll('.carousel-item'));
  const activeNode = nodes[state.carouselIndex];
  if (!activeNode || !state.carouselItems.length) return;

  function advance() {
    if (state.carouselGeneration !== gen) return;
    state.carouselTimer = null;
    state.carouselIndex = (state.carouselIndex + 1) % state.carouselItems.length;
    activateCarouselItem(state.carouselIndex);
    scheduleNextSlide();
  }

  const video = activeNode.querySelector('video');
  if (video) {
    video.addEventListener('ended', advance, { once: true });
  } else {
    const durationMs = Math.max(2, Number(state.config.media.carousel_seconds || 8)) * 1000;
    state.carouselTimer = window.setTimeout(advance, durationMs);
  }
}

function renderCarousel(items) {
  clearCarousel();
  state.carouselItems = items;
  if (!items.length) { el.carouselEmpty.hidden = false; return; }
  el.carouselEmpty.hidden = true;
  items.forEach((item, index) => {
    const wrap = document.createElement('div');
    wrap.className = `carousel-item${index === 0 ? ' active' : ''}`;
    if (item.type === 'video') {
      const video = document.createElement('video');
      video.src = item.url; video.muted = true; video.playsInline = true;
      if (index === 0) video.autoplay = true;
      wrap.appendChild(video);
    } else {
      const img = document.createElement('img');
      img.src = item.url; img.alt = item.name || 'Рекламный файл';
      wrap.appendChild(img);
    }
    el.carouselStage.appendChild(wrap);
  });
  scheduleNextSlide();
}

async function loadMedia() {
  const data = await api('/api/media/items');
  renderCarousel(data.items || []);
}

async function loadMediaFiles() {
  try {
    const data = await api('/api/media/items');
    const items = data.items || [];
    if (!items.length) {
      el.mediaFilesList.innerHTML = '<div class="media-files-empty">Нет файлов в папке</div>';
      return;
    }
    el.mediaFilesList.innerHTML = items.map(item => `
      <div class="media-file-item" data-name="${escapeHtml(item.name)}">
        <span class="media-file-icon">${item.type === 'video' ? '🎬' : '🖼️'}</span>
        <span class="media-file-name" title="${escapeHtml(item.name)}">${escapeHtml(item.name)}</span>
        <span class="media-file-size">${formatBytes(item.size_bytes)}</span>
        <button class="media-file-del" type="button" data-name="${escapeHtml(item.name)}">Удалить</button>
      </div>
    `).join('');
    el.mediaFilesList.querySelectorAll('.media-file-del').forEach(btn => {
      btn.addEventListener('click', () => deleteMedia(btn.dataset.name));
    });
  } catch (err) {
    el.mediaFilesList.innerHTML = `<div class="media-files-empty">Ошибка загрузки: ${escapeHtml(err.message)}</div>`;
  }
}

async function uploadMedia() {
  const fileInput = el.mediaFileInput;
  if (!fileInput.files || !fileInput.files.length) {
    el.settingsStatus.textContent = 'Выберите файл для загрузки';
    return;
  }
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);
  el.uploadMediaButton.disabled = true;
  el.settingsStatus.textContent = 'Загрузка файла…';
  try {
    const response = await fetch('/api/media/upload', { method: 'POST', body: formData });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || `HTTP ${response.status}`);
    }
    fileInput.value = '';
    await loadMediaFiles();
    await loadMedia();
    el.settingsStatus.textContent = `Файл «${file.name}» загружен`;
  } catch (err) {
    el.settingsStatus.textContent = `Ошибка загрузки: ${err.message}`;
  } finally {
    el.uploadMediaButton.disabled = false;
  }
}

async function deleteMedia(name) {
  if (!confirm(`Удалить файл «${name}»?`)) return;
  el.settingsStatus.textContent = 'Удаление…';
  try {
    await api(`/api/media/file/${encodeURIComponent(name)}`, { method: 'DELETE' });
    await loadMediaFiles();
    await loadMedia();
    el.settingsStatus.textContent = `Файл «${name}» удалён`;
  } catch (err) {
    el.settingsStatus.textContent = `Ошибка удаления: ${err.message}`;
  }
}

function formatLocalDate(value) {
  if (!value) return '—';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString('ru-RU');
}

async function loadParkingStatus() {
  try {
    const data = await api('/api/parking/status');
    renderPlaces(data);
    const fetchedAt = data.fetched_at || data.generated_at;
  } catch (error) {
    renderPlaces({ levels: [], total_free: 0 });
  }
}

function scheduleParkingReload() {
  if (state.parkingTimer) { window.clearInterval(state.parkingTimer); }
  loadParkingStatus();
  state.parkingTimer = window.setInterval(loadParkingStatus, 15000);
}

function scheduleModeCheck() {
  if (state.modeCheckTimer) window.clearInterval(state.modeCheckTimer);
  state.modeCheckTimer = window.setInterval(() => {
    if (state.config) applyDisplayMode(state.config);
  }, 60000);
}

function openSettings() {
  state.settingsOpen = true;
  el.settingsBackdrop.style.display = 'flex';
  loadMediaFiles();
}

function closeSettings() {
  state.settingsOpen = false;
  el.settingsBackdrop.style.display = 'none';
}

function switchTab(name) {
  tabButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.tab === name));
  tabPanels.forEach(panel => panel.classList.toggle('active', panel.dataset.panel === name));
  if (name === 'media') loadMediaFiles();
}

async function saveSettings() {
  try {
    const data = await api('/api/settings', { method: 'PUT', body: JSON.stringify(readForm()) });
    state.config = data.config;
    state.metadata = data.metadata;
    renderConfig(state.config);
    fillForm(state.config, state.metadata);
    await loadRawYaml();
    await loadMedia();
    scheduleParkingReload();
    el.settingsStatus.textContent = data.message || 'Настройки сохранены';
  } catch (error) {
    el.settingsStatus.textContent = `Ошибка сохранения: ${error.message}`;
  }
}

async function reloadFromDisk() {
  try {
    const data = await api('/api/settings/reload', { method: 'POST' });
    state.config = data.config;
    state.metadata = data.metadata;
    renderConfig(state.config);
    fillForm(state.config, state.metadata);
    await loadRawYaml();
    await loadMedia();
    scheduleParkingReload();
    el.settingsStatus.textContent = data.message || 'YAML перечитан';
  } catch (error) {
    el.settingsStatus.textContent = `Ошибка перечитывания: ${error.message}`;
  }
}

async function testParser() {
  try {
    const data = await api('/api/parking/test', {
      method: 'POST',
      body: JSON.stringify({
        server: fields.parserServerInput.value.trim(),
        path: fields.parserPathInput.value.trim(),
        token: fields.parserTokenInput.value.trim(),
      }),
    });
    el.parserTestOutput.textContent = JSON.stringify(data, null, 2);
    el.settingsStatus.textContent = 'Проверка парсера выполнена успешно';
  } catch (error) {
    el.parserTestOutput.textContent = error.message;
    el.settingsStatus.textContent = `Проверка не удалась: ${error.message}`;
  }
}

function bindTabs() {
  tabButtons.forEach(btn => btn.addEventListener('click', () => switchTab(btn.dataset.tab)));
}

function bindDirtyTracking() {
  Object.values(fields).forEach(node => {
    if (!node || typeof node.addEventListener !== 'function') return;
    node.addEventListener('input', markDirty);
    node.addEventListener('change', markDirty);
  });
}

function bindSettingsAccess() {
  el.settingsHotspot.addEventListener('click', openSettings);
  el.settingsClose.addEventListener('click', closeSettings);
  el.cancelSettingsButton.addEventListener('click', closeSettings);
  el.settingsBackdrop.addEventListener('click', event => { if (event.target === el.settingsBackdrop) closeSettings(); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && state.settingsOpen) { closeSettings(); }
  });
  el.saveSettingsButton.addEventListener('click', saveSettings);
  el.reloadDiskButton.addEventListener('click', reloadFromDisk);
  el.testParserButton.addEventListener('click', testParser);
  el.uploadMediaButton.addEventListener('click', uploadMedia);
}

async function bootstrap() {
  bindTabs();
  bindDirtyTracking();
  bindSettingsAccess();
  switchTab('general');
  try {
    await loadSettings();
    await loadRawYaml();
    await loadMedia();
    scheduleParkingReload();
    scheduleModeCheck();
  } catch (error) {
    el.settingsStatus.textContent = `Ошибка инициализации: ${error.message}`;
  }
}

bootstrap();
