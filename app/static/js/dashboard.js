// --- State ---
const state = {
    lang: 'en',
    theme: 'dark',
    config: {},
    lastMessageTimestamp: 0,
    pollingInterval: null
};

// --- I18n ---
const i18n = {
    en: {
        subtitle: "Manage your AI Node",
        char_settings: "Character Settings",
        char_name: "Character Name",
        char_persona: "Persona",
        sys_prompt: "System Prompt",
        llm_settings: "LLM Settings",
        llm_model: "Model Name",
        llm_url: "Base URL",
        trans_settings: "Translation",
        trans_enable: "Enable Auto-Translation",
        trans_target: "Target Language",
        room_settings: "Room & Discovery",
        room_name: "Room Name",
        room_desc: "Description",
        max_visitors: "Max Visitors",
        auto_announce: "Auto-Publish to Discovery",
        discovery_url: "Discovery API URL",
        active_rooms: "Active Rooms",
        room_status: "Room Status",
        close_room: "CLOSE ROOM",
        open_room: "OPEN ROOM",
        security_header: "Security",
        api_key_label: "API Key (Optional)",
        api_key_placeholder: "Wait for authorization...",
        tab_dashboard: "Dashboard",
        tab_lobby: "Lobby",
        tab_room: "My Room",
        capacity: "Capacity",
        save_btn: "Save Configuration",
        saving: "Saving...",
        saved: "Saved!",
        error: "Error",
        refresh: "Refresh",
        connect_btn: "Connect",
        host_input_placeholder: "Speak as Host...",
        send_btn: "Send",
        agent_header: "Agent Settings",
        max_turns: "Max Connection Turns",
        send_agent_btn: "Send Agent",
        send_agent_confirm: "Send your agent to visit {url}?",
        agent_sent: "Agent Dispatched! Check your chat log for updates.",
        agent_fail: "Failed to dispatch agent.",

        // Help
        help_llm_model: "Model ID compatible with LiteLLM (e.g. gpt-4o, ollama/llama3).",
        help_llm_url: "Base URL for API (e.g. https://api.openai.com/v1).",
        help_char_name: "Name displayed to visitors.",
        help_char_persona: "Personality instructions.",
        help_sys_prompt: "Base behavior rules.",
        help_trans_enable: "Real-time translation of incoming/outgoing messages.",
        help_max_turns: "Agent ends conversation after this many exchanges.",
        help_trans_enable: "Real-time translation of incoming/outgoing messages.",
        help_max_turns: "Agent ends conversation after this many exchanges.",
        help_api_key: "Set an arbitrary string and share it only with users you trust.",
        help_discovery_url: "Basically, please use the registered URL.",

        // Detection
        detect_btn: "Scan",
        detected_label: "Detected Models",
        detected_placeholder: "Manual Input (Select to auto-fill)",
        scanning: "Scanning...",
        scan_success: "Found {n} models",
        no_models: "No local models found",

        // Logs
        tab_logs: "Logs",
        logs_title: "Conversation Logs",
        delete_logs: "Delete All Logs",
        select_session: "Select a session to view details",
        log_deleted: "All logs deleted.",
        confirm_delete: "Are you sure you want to delete ALL logs? This cannot be undone.",
        confirm_delete: "Are you sure you want to delete ALL logs? This cannot be undone.",
        confirm_delete_session: "Delete this entire session?",

        // Password Modal
        enter_password: "Enter Room Password",
        password_desc: "This room is secured. Please enter the API Key.",
        cancel: "Cancel",
        submit: "Submit",

        // Lore
        tab_lore: "Lore",
        lore_title: "Lorebook (World Info)",
        add_lore: "Add Entry",
        lore_keyword: "Keyword",
        lore_content: "Description / Definition",
        lore_modal_title: "Edit Lore",
        lore_select_hint: "Select an entry to view/edit",
        save_btn: "Save",

        // Character Card
        character_card: "Card",
        character_card_title: "Character Card",
        card_import: "Import",
        card_export: "Export",
        drop_zone_text: "Drag & Drop PNG here\nor click to select",
        card_format_hint: "Supports SillyTavern/Chub V2 format",
        export_desc: "Export current character settings as a PNG character card.",
        export_btn: "Export PNG",
        card_preview: "Preview",
        preview_name: "Name",
        preview_persona: "Description / Persona",
        preview_system: "System Prompt",
        apply_import: "Apply Import"
    },
    ja: {
        subtitle: "AIノード管理",
        char_settings: "キャラクター設定",
        char_name: "名前",
        char_persona: "ペルソナ（性格）",
        sys_prompt: "システムプロンプト",
        llm_settings: "LLM設定",
        llm_model: "モデル名",
        llm_url: "ベースURL",
        trans_settings: "翻訳設定",
        trans_enable: "自動翻訳を有効化",
        trans_target: "翻訳先の言語",
        room_settings: "ルーム公開設定",
        room_name: "ルーム名",
        room_desc: "紹介文",
        max_visitors: "最大入室数",
        auto_announce: "ロビーに自動公開",
        discovery_url: "Discovery API URL",
        active_rooms: "公開中のルーム",
        room_status: "ルーム状態",
        close_room: "ルームを閉じる",
        open_room: "ルームを開ける",
        security_header: "セキュリティ",
        api_key_label: "APIキー (任意)",
        api_key_placeholder: "認証待ち...",
        tab_dashboard: "設定",
        tab_lobby: "ロビー",
        tab_room: "マイルーム",
        capacity: "人数",
        save_btn: "設定を保存",
        saving: "保存中...",
        saved: "保存しました！",
        error: "エラーが発生しました",
        refresh: "更新",
        connect_btn: "接続",
        host_input_placeholder: "ホストとして発言...",
        send_btn: "送信",
        agent_header: "エージェント設定 (AI接続)",
        max_turns: "最大会話数 (Max Turns)",
        send_agent_btn: "AI同士で会話",
        send_agent_confirm: "{url} にAIを派遣しますか？",
        agent_sent: "AIを派遣しました！チャットログを確認してください。",
        agent_fail: "派遣に失敗しました。",

        // Help
        help_llm_model: "LiteLLM互換のモデル対応ID（例: gpt-4o, ollama/llama3）",
        help_llm_url: "APIのベースURL（例: https://api.openai.com/v1）",
        help_char_name: "訪問者に表示されるAIの名前",
        help_char_persona: "AIの性格や振る舞いの指示書",
        help_sys_prompt: "根本的な動作ルール",
        help_trans_enable: "送受信メッセージをリアルタイムで翻訳します",
        help_max_turns: "この回数だけ会話を往復すると相手のAIは帰還します",
        help_trans_enable: "送受信メッセージをリアルタイムで翻訳します",
        help_api_key: "任意の文字列を設定して、共有したいユーザーにだけ伝えてください",
        help_discovery_url: "基本的には、初期登録のURLをお使いください",

        // Detection
        detect_btn: "スキャン",
        detected_label: "検出されたモデル",
        detected_placeholder: "手動入力 (選択すると自動入力)",
        scanning: "スキャン中...",
        scan_success: "{n} 個のモデルが見つかりました",
        no_models: "ローカルモデルが見つかりませんでした",

        // Logs
        tab_logs: "ログ",
        logs_title: "会話ログ",
        delete_logs: "全ログ削除",
        select_session: "セッションを選択して詳細を表示",
        log_deleted: "全てのログを削除しました。",
        confirm_delete: "本当に全てのログを削除しますか？この操作は取り消せません。",
        confirm_delete_session: "このセッション履歴を削除しますか？",

        // Password Modal
        enter_password: "ルームパスワード入力",
        password_desc: "このルームは保護されています。APIキーを入力してください。",
        cancel: "キャンセル",
        submit: "送信",

        // Lore
        tab_lore: "用語集",
        lore_title: "用語集 (Lorebook)",
        add_lore: "追加",
        lore_keyword: "キーワード",
        lore_content: "説明・定義",
        lore_modal_title: "用語の編集",
        lore_select_hint: "項目を選択して編集",
        save_btn: "保存",

        // Character Card
        character_card: "カード",
        character_card_title: "キャラクターカード",
        card_import: "インポート",
        card_export: "エクスポート",
        drop_zone_text: "PNGをドラッグ＆ドロップ\nまたはクリックして選択",
        card_format_hint: "SillyTavern/Chub V2形式対応",
        export_desc: "現在のキャラクター設定をPNGカードとしてエクスポートします。",
        export_btn: "PNGをダウンロード",
        card_preview: "プレビュー",
        preview_name: "名前",
        preview_persona: "説明 / ペルソナ",
        preview_system: "システムプロンプト",
        apply_import: "インポートを適用"
    }
};

// --- Tabs ---
function switchTab(tabId) {
    // Update UI
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`section-${tabId}`).classList.remove('hidden');

    // Update Tab style
    const activeClass = state.theme === 'dark' ? 'bg-slate-700' : 'bg-white shadow';
    const inactiveClass = 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300';

    ['dashboard', 'lobby', 'room', 'logs', 'lore'].forEach(t => {
        const btn = document.getElementById(`tab-${t}`);
        if (t === tabId) {
            btn.className = `px-4 py-2 rounded-md text-sm font-bold transition-transform transform scale-105 shadow ${state.theme === 'dark' ? 'bg-slate-700 text-white' : 'bg-white text-slate-800'}`;
        } else {
            btn.className = `px-4 py-2 rounded-md text-sm font-medium transition-colors text-slate-500 hover:bg-slate-300 dark:hover:bg-slate-700`;
        }
    });

    // Logic
    if (tabId === 'lobby') {
        fetchRooms();
    }

    // Logs Load
    if (tabId === 'logs') {
        refreshLogs();
    }
    if (tabId === 'logs') {
        refreshLogs();
    }
    if (tabId === 'lore') {
        renderLoreList();
    }
    if (tabId === 'room') {
        startChatPolling();
    } else {
        stopChatPolling();
    }
}

// --- Theme ---
function toggleTheme() {
    const html = document.documentElement;
    if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        html.classList.add('light');
        state.theme = 'light';
        localStorage.setItem('theme', 'light');
        document.getElementById('theme-toggle').innerText = '☀️';
    } else {
        html.classList.add('dark');
        html.classList.remove('light');
        state.theme = 'dark';
        localStorage.setItem('theme', 'dark');
        document.getElementById('theme-toggle').innerText = '🌙';
    }
    // Re-apply tab styles
    const currentTab = ['dashboard', 'lobby', 'room'].find(t => !document.getElementById(`section-${t}`).classList.contains('hidden'));
    switchTab(currentTab);
}

// --- Exports ---
window.state = state;
window.i18n = i18n;
window.updateTexts = updateTexts;
window.switchTab = switchTab;
window.toggleTheme = toggleTheme;

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();

    // Theme Init
    const savedTheme = localStorage.getItem('theme') || 'dark';
    state.theme = savedTheme;
    if (savedTheme === 'dark') document.documentElement.classList.add('dark');
    else {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
        document.getElementById('theme-toggle').innerText = '☀️';
    }
    switchTab('dashboard');

    // Language Init
    const savedLang = localStorage.getItem('lang') || 'en';
    document.getElementById('lang-select').value = savedLang;
    updateTexts(savedLang);
});

// --- I18n ---
function updateTexts(lang) {
    console.log('[Dashboard] updateTexts called with:', lang);
    state.lang = lang;
    const texts = i18n[lang];
    if (!texts) {
        console.error('[Dashboard] No texts found for lang:', lang);
        return;
    }

    const elements = document.querySelectorAll('[data-i18n]');
    console.log('[Dashboard] Found i18n elements:', elements.length);

    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (texts[key]) {
            el.innerText = texts[key];
        } else {
            console.warn('[Dashboard] Missing key:', key);
        }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (texts[key]) el.placeholder = texts[key];
    });
    // Update dynamic elements
    // Update dynamic elements
    updateRoomStatusUI(state.is_open_cache !== undefined ? state.is_open_cache : true);
}

// --- Config Logic ---
async function fetchRoomStatus() {
    try {
        const res = await fetch('/api/room/status');
        const data = await res.json();
        updateRoomStatusUI(data.is_open, data.public_url);
    } catch (e) { console.error(e); }
}

async function toggleRoom() {
    try {
        const res = await fetch('/api/room/toggle', { method: 'POST' });
        const data = await res.json();
        updateRoomStatusUI(data.is_open, data.public_url);
    } catch (e) { console.error(e); }
}

function updateRoomStatusUI(isOpen, publicUrl) {
    const statusText = document.getElementById('room-status-text');
    const toggleBtn = document.getElementById('room-toggle-btn');
    const headerToggleBtn = document.getElementById('room-toggle-btn-header');
    const urlEl = document.getElementById('room-public-url');
    const liveBadge = document.getElementById('room-live-badge');

    // Cache state
    state.is_open_cache = isOpen;

    if (publicUrl) state.public_url_cache = publicUrl;
    else if (state.public_url_cache) publicUrl = state.public_url_cache;

    if (isOpen) {
        statusText.innerText = 'OPEN';
        statusText.className = 'text-xs text-green-500 font-bold uppercase';

        const closeText = i18n[state.lang].close_room;
        const closeClass = 'px-3 py-1 bg-red-700 hover:bg-red-800 text-white text-xs font-bold rounded shadow transition-transform hover:scale-105';

        toggleBtn.innerText = closeText;
        toggleBtn.className = closeClass;

        if (headerToggleBtn) {
            headerToggleBtn.innerText = closeText;
            headerToggleBtn.className = closeClass;
        }

        if (publicUrl) {
            urlEl.textContent = publicUrl;
            urlEl.href = publicUrl;
            urlEl.classList.remove('hidden');
        }

        // Sync Live Badge
        if (liveBadge) {
            liveBadge.innerText = "LIVE";
            liveBadge.className = "px-2 py-1 rounded bg-green-500/10 text-green-500 text-xs border border-green-500/20";
            liveBadge.classList.remove('hidden');
        }
    } else {
        statusText.innerText = 'CLOSED';
        statusText.className = 'text-xs text-red-500 font-bold uppercase';

        const openText = i18n[state.lang].open_room;
        const openClass = 'px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-xs font-bold rounded shadow transition-transform hover:scale-105';

        toggleBtn.innerText = openText;
        toggleBtn.className = openClass;

        if (headerToggleBtn) {
            headerToggleBtn.innerText = openText;
            headerToggleBtn.className = openClass;
        }

        urlEl.classList.add('hidden');

        // Sync Live Badge
        if (liveBadge) {
            liveBadge.innerText = "OFFLINE";
            liveBadge.className = "px-2 py-1 rounded bg-slate-500/10 text-slate-400 text-xs border border-slate-500/20";
        }
    }
}

async function loadConfig() {
    try {
        const res = await fetch('/api/config');
        const config = await res.json();
        state.config = config;

        // Dashboard Lang
        if (config.dashboard && config.dashboard.language) {
            document.getElementById('lang-select').value = config.dashboard.language;
            updateTexts(config.dashboard.language);
        }

        // Fill Forms
        document.getElementById('char-name').value = config.character.name || "";
        document.getElementById('char-persona').value = config.character.persona || "";
        document.getElementById('char-prompt').value = config.character.system_prompt || "";
        document.getElementById('llm-model').value = config.llm.model || "";
        document.getElementById('llm-url').value = config.llm.base_url || "";

        if (config.translation) {
            document.getElementById('trans-enabled').checked = config.translation.enabled;
            document.getElementById('trans-target').value = config.translation.target_lang || 'ja';
        }
        if (config.room) {
            document.getElementById('room-name').value = config.room.name || "";
            document.getElementById('room-desc').value = config.room.description || "";
            document.getElementById('room-capacity').value = config.room.max_visitors || 5;
            document.getElementById('auto-announce').checked = config.room.auto_announce || false;
            document.getElementById('discovery-url').value = config.room.discovery_api_url || "";

            document.getElementById('room-display-name').innerText = config.room.name || "My Room";
        }
        if (config.agent) {
            document.getElementById('agent-max-turns').value = config.agent.max_turns || 10;
        }

        if (config.security) {
            document.getElementById('api-key').value = config.security.api_key || "";
        }

    } catch (e) { console.error(e); }
}

async function saveConfig() {
    // Gather data...
    const newConfig = { ...state.config };
    if (!newConfig.dashboard) newConfig.dashboard = {};
    newConfig.dashboard.language = document.getElementById('lang-select').value;

    newConfig.character.name = document.getElementById('char-name').value;
    newConfig.character.persona = document.getElementById('char-persona').value;
    newConfig.character.system_prompt = document.getElementById('char-prompt').value;

    newConfig.llm.model = document.getElementById('llm-model').value;
    newConfig.llm.base_url = document.getElementById('llm-url').value;

    if (!newConfig.translation) newConfig.translation = {};
    newConfig.translation.enabled = document.getElementById('trans-enabled').checked;
    newConfig.translation.target_lang = document.getElementById('trans-target').value;

    if (!newConfig.room) newConfig.room = {};
    newConfig.room.name = document.getElementById('room-name').value;
    newConfig.room.description = document.getElementById('room-desc').value;
    newConfig.room.max_visitors = parseInt(document.getElementById('room-capacity').value) || 5;
    newConfig.room.auto_announce = document.getElementById('auto-announce').checked;
    newConfig.room.discovery_api_url = document.getElementById('discovery-url').value;

    if (!newConfig.agent) newConfig.agent = {};
    newConfig.agent.max_turns = parseInt(document.getElementById('agent-max-turns').value) || 10;

    if (!newConfig.security) newConfig.security = {};
    const apiKeyInput = document.getElementById('api-key').value.trim();
    newConfig.security.api_key = apiKeyInput === "" ? null : apiKeyInput;

    // Send
    const btn = document.getElementById('save-btn');
    btn.innerText = i18n[state.lang].saving;
    try {
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newConfig)
        });
        if (res.ok) {
            state.config = newConfig;
            btn.innerText = i18n[state.lang].saved;
            setTimeout(() => btn.innerText = i18n[state.lang].save_btn, 2000);
            document.getElementById('room-display-name').innerText = newConfig.room.name;
        }
    } catch (e) {
        btn.innerText = i18n[state.lang].error;
    }
}


// --- Detection Logic ---
async function scanLLMs() {
    const btn = document.getElementById('scan-btn');
    const select = document.getElementById('detected-models');
    const icon = btn.querySelector('i');
    const label = btn.querySelector('span'); // if visible

    // UI Loading
    icon.classList.add('fa-spin');
    const originalTitle = btn.title;
    btn.title = i18n[state.lang].scanning;

    try {
        const res = await fetch('/api/llm/detect');
        const models = await res.json();

        // Clear options
        select.innerHTML = `<option value="">${i18n[state.lang].detected_placeholder}</option>`;

        if (models.length === 0) {
            alert(i18n[state.lang].no_models);
        } else {
            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = JSON.stringify({ id: m.model_id, url: m.base_url });
                opt.textContent = m.label;
                select.appendChild(opt);
            });
            // alert(i18n[state.lang].scan_success.replace('{n}', models.length));
        }

    } catch (e) {
        console.error("Scan failed", e);
        alert(i18n[state.lang].error);
    } finally {
        icon.classList.remove('fa-spin');
        btn.title = originalTitle;
    }
}

function applyDetectedModel() {
    const select = document.getElementById('detected-models');
    const val = select.value;
    if (!val) return;

    try {
        const data = JSON.parse(val);
        document.getElementById('llm-model').value = data.id;
        document.getElementById('llm-url').value = data.url;
    } catch (e) {
        console.error(e);
    }
}

// --- Lobby Logic ---
async function fetchRooms() {
    const list = document.getElementById('rooms-list');
    try {
        list.innerHTML = `<p class="col-span-full text-center text-slate-500">Refreshing...</p>`;
        const res = await fetch('/api/discovery/rooms');
        const rooms = await res.json();

        if (rooms.length === 0) {
            list.innerHTML = `<div class="col-span-full text-center text-slate-500 p-8 glass rounded-xl">No active rooms found.</div>`;
            return;
        }

        list.innerHTML = rooms.map(room => `
            <div class="glass p-4 rounded-xl border border-slate-700/50 hover:border-blue-500/50 transition-all group relative overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div class="relative z-10 flex justify-between items-start">
                    <div>
                        <h3 class="font-bold text-lg text-blue-400 mb-1">
                            ${room.metadata?.locked ? '<i class="fas fa-lock text-yellow-500 mr-2" title="Auth Required"></i>' : ''}
                            ${room.name || "Unknown Room"}
                        </h3>
                        <div class="flex items-center gap-2 mb-2">
                            <span class="text-xs bg-slate-700 px-2 py-0.5 rounded text-slate-300">${i18n[state.lang].capacity}: ${room.metadata?.max_visitors || "?"}</span>
                            <span class="text-xs bg-slate-700 px-2 py-0.5 rounded text-slate-300">${room.metadata?.character || "Standard AI"}</span>
                            ${room.metadata?.model ? `<span class="text-xs bg-purple-900/50 border border-purple-500/30 px-2 py-0.5 rounded text-purple-100 font-mono">${room.metadata.model}</span>` : ''}
                        </div>
                        <p class="text-sm text-slate-400 mb-2 line-clamp-2 h-10">${room.metadata?.description || "No description provided."}</p>
                        <p class="text-xs text-slate-500 font-mono truncate w-64">${room.url}</p>
                    <div class="mt-4 flex justify-end gap-2">
                        ${room.metadata?.locked
                ? `<button onclick="openPasswordModal('agent', '${room.url}')" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded font-bold shadow transition-transform hover:scale-105 whitespace-nowrap text-sm">
                                <i class="fas fa-robot mr-1"></i> ${i18n[state.lang].send_agent_btn}
                               </button>
                               <button onclick="openPasswordModal('connect', '${room.url}')" class="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded font-bold shadow transition-transform hover:scale-105 whitespace-nowrap text-sm">
                                <i class="fas fa-key mr-1"></i> ${i18n[state.lang].connect_btn}
                               </button>`
                : `<button onclick="sendAgent('${room.url}')" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded font-bold shadow transition-transform hover:scale-105 whitespace-nowrap text-sm">
                                <i class="fas fa-robot mr-1"></i> ${i18n[state.lang].send_agent_btn}
                               </button>
                               <a href="${room.url}" target="_blank" class="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded font-bold shadow transition-transform hover:scale-105 whitespace-nowrap text-sm">
                                ${i18n[state.lang].connect_btn}
                               </a>`
            }
                    </div>
            </div>
        `).join('');
    } catch (e) {
        list.innerHTML = `<p class="text-red-400">Failed to load rooms.</p>`;
    }
}

// --- Room/Chat Logic ---

function renderMessage(msg) {
    const container = document.getElementById('chat-container');
    const isMe = msg.sender_id === state.config.instance_id || msg.sender_id === 'HOST'; // Assuming host is me
    // Or strictly, if it is MY character responding.
    // Actually, we distinguish "Visitor" vs "Host" (Me/My AI).
    // msg.sender_id checks...
    // Let's rely on sender name or simple logic for now. 
    // Better: 'visitor' role vs 'host' role?
    // The backend logs: sender="visitor" or "host". 
    // The memory structure has "sender_id".

    // Heuristic for bubble side:
    const isHost = (msg.sender_name === state.config.character.name) || msg.is_human === true;

    const alignClass = isHost ? 'justify-end' : 'justify-start';
    const bubbleClass = isHost
        ? 'bg-blue-600 text-white rounded-br-none'
        : 'bg-slate-700 text-slate-200 rounded-bl-none';

    const timeStr = new Date(msg.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const html = `
        <div class="flex ${alignClass} mb-4 anime-fade-in">
            <div class="max-w-[70%]">
                <div class="flex items-end gap-2 ${isHost ? 'flex-row-reverse' : ''}">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-gray-400 to-gray-600 flex items-center justify-center text-xs font-bold text-white shrink-0">
                        ${msg.sender_name[0]}
                    </div>
                    <div class="flex flex-col ${isHost ? 'items-end' : 'items-start'}">
                        <span class="text-xs text-slate-400 mb-1 px-1 flex items-center gap-2">
                            ${msg.sender_name}
                            ${msg.model ? `<span class="text-[10px] bg-white/10 px-1 rounded border border-white/20 font-mono">${msg.model}</span>` : ''}
                        </span>
                        <div class="${bubbleClass} px-4 py-2 rounded-2xl shadow-md text-sm leading-relaxed">
                            ${msg.content}
                        </div>
                        <span class="text-[10px] text-slate-500 mt-1 px-1">${timeStr}</span>
                    </div>
                </div>
            </div>
        </div>
    `;

    const div = document.createElement('div');
    div.innerHTML = html;
    container.appendChild(div.firstElementChild);
    container.scrollTo(0, container.scrollHeight);
}

async function pollMessages() {
    try {
        const url = `/api/room/messages?since=${state.lastMessageTimestamp}`;
        const res = await fetch(url);
        if (!res.ok) return;
        const msgs = await res.json();

        msgs.sort((a, b) => a.timestamp - b.timestamp);

        msgs.forEach(msg => {
            if (msg.timestamp > state.lastMessageTimestamp) {
                renderMessage(msg);
                state.lastMessageTimestamp = msg.timestamp;
            }
        });
    } catch (e) { console.error("Poll error", e); }
}

function startChatPolling() {
    if (state.pollingInterval) return;
    pollMessages(); // Initial fetch
    state.pollingInterval = setInterval(pollMessages, 3000);
}

function stopChatPolling() {
    if (state.pollingInterval) {
        clearInterval(state.pollingInterval);
        state.pollingInterval = null;
    }
}

async function sendHostMessage() {
    const input = document.getElementById('host-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';

    // Optimistic render? No, let's wait for poll or just append.
    // Appending optimistically is better UX.
    // renderMessage({
    //     sender_name: state.config.character.name + " (You)",
    //     content: text,
    //     timestamp: Date.now()/1000,
    //     is_human: true
    // });

    try {
        await fetch('/api/host/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        // Poll will catch it shortly
        pollMessages();
    } catch (e) {
        console.error("Send error", e);
    }
}

async function sendAgent(url) {
    const texts = i18n[state.lang];
    const msg = texts.send_agent_confirm.replace('{url}', url);
    if (!confirm(msg)) return;

    try {
        const res = await fetch('/api/room/connect_agent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        if (res.ok) {
            alert(texts.agent_sent);
            switchTab('chat');
        } else {
            alert(texts.agent_fail);
        }
    } catch (e) {
        console.error(e);
        alert(texts.agent_fail);
    }
}


// --- Password Modal Logic ---
let passwordModalContext = { action: null, url: null };

function openPasswordModal(action, url) {
    passwordModalContext = { action, url };
    document.getElementById('modal-password-input').value = '';
    document.getElementById('password-modal').classList.remove('hidden');
    document.getElementById('modal-password-input').focus();
}

function closePasswordModal() {
    document.getElementById('password-modal').classList.add('hidden');
    passwordModalContext = { action: null, url: null };
}

function submitPassword() {
    const pwd = document.getElementById('modal-password-input').value.trim();
    if (!pwd) return;

    const { action, url } = passwordModalContext;
    if (!action || !url) return;

    // Append key param
    // Check if url already has params
    const separator = url.includes('?') ? '&' : '?';
    const finalUrl = `${url}${separator}key=${encodeURIComponent(pwd)}`;

    closePasswordModal();

    if (action === 'connect') {
        window.open(finalUrl, '_blank');
    } else if (action === 'agent') {
        sendAgent(finalUrl);
    }
}

// --- Lorebook Logic ---
let allLoreEntries = [];

async function renderLoreList() {
    const list = document.getElementById('lore-list');
    const search = document.getElementById('lore-search').value.toLowerCase();

    try {
        const res = await fetch('/api/lore');
        allLoreEntries = await res.json();
    } catch (e) { console.error(e); }

    const filtered = allLoreEntries.filter(e => e.keyword.toLowerCase().includes(search));

    if (filtered.length === 0) {
        list.innerHTML = `<div class="text-center text-slate-400 text-xs mt-4">No entries found.</div>`;
        return;
    }

    list.innerHTML = filtered.map(item => `
        <div onclick="selectLore('${item.keyword}')" class="p-3 bg-white dark:bg-slate-800 rounded shadow-sm cursor-pointer hover:bg-blue-50 dark:hover:bg-slate-700/50 transition border-l-4 ${item.source === 'host' ? 'border-blue-500' : 'border-green-500'}">
            <div class="flex justify-between items-center">
                <span class="font-bold text-slate-700 dark:text-slate-200">${item.keyword}</span>
                <span class="text-[10px] uppercase font-mono px-1 rounded ${item.source === 'host' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'}">${item.source}</span>
            </div>
            <p class="text-xs text-slate-500 line-clamp-1 mt-1">${item.content}</p>
        </div>
    `).join('');
}

function selectLore(keyword) {
    const item = allLoreEntries.find(e => e.keyword === keyword);
    if (!item) return;
    openLoreModal(item);
}

function openLoreModal(item = null) {
    const modal = document.getElementById('lore-modal');
    modal.classList.remove('hidden');

    if (item) {
        document.getElementById('lore-modal-title').innerText = i18n[state.lang].lore_modal_title || 'Edit Lore';
        document.getElementById('lore-keyword').value = item.keyword;
        document.getElementById('lore-keyword').disabled = true; // Key cannot be changed easily for now
        document.getElementById('lore-content').value = item.content;
    } else {
        document.getElementById('lore-modal-title').innerText = i18n[state.lang].add_lore || 'Add Lore';
        document.getElementById('lore-keyword').value = '';
        document.getElementById('lore-keyword').disabled = false;
        document.getElementById('lore-content').value = '';
    }
}

function closeLoreModal() {
    document.getElementById('lore-modal').classList.add('hidden');
}

async function saveLoreEntry() {
    const keyword = document.getElementById('lore-keyword').value.trim();
    const content = document.getElementById('lore-content').value.trim();
    if (!keyword || !content) return;

    try {
        const res = await fetch('/api/lore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keyword, content, source: 'host' })
        });
        if (res.ok) {
            closeLoreModal();
            renderLoreList();
        }
    } catch (e) { alert('Error saving lore'); }
}

function openTeachModal() {
    // Re-use lore modal but for "Teaching" (Host manually teaching)
    // Actually, the "Teach" button in Chat UI is for sending the !learn command, 
    // OR just adding to DB?
    // If we add to DB directly, it's same as "Add Lore".
    // User asked for "Teach AI command... via button".
    // Let's implement it as: Open a modal -> Input -> Send "!learn KW Content" message to chat.
    // This allows the AI to react to it as if it was a command in chat.

    const modal = document.getElementById('lore-modal');
    modal.classList.remove('hidden');
    document.getElementById('lore-modal-title').innerText = "Teach AI (Send Command)";
    document.getElementById('lore-keyword').value = '';
    document.getElementById('lore-keyword').disabled = false;
    document.getElementById('lore-content').value = '';

    // Override Save button to behave as Send Command
    const saveBtn = modal.querySelector('button[onclick="saveLoreEntry()"]');
    saveBtn.setAttribute('onclick', 'sendTeachCommand()');
    saveBtn.innerText = "Teach";
}

async function sendTeachCommand() {
    const keyword = document.getElementById('lore-keyword').value.trim();
    const content = document.getElementById('lore-content').value.trim();
    if (!keyword || !content) return;

    // Construct command
    const cmd = `!learn ${keyword} ${content}`;

    // Send as Host Message
    // Reuse sendHostMessage logic but with custom text
    try {
        await fetch('/api/room/chat', { // Assuming endpoint for host chat logic? 
            // Wait, sendHostMessage() in dashboard simply calls... wait, where is sendHostMessage logic?
            // Ah, sendHostMessage() is in lines 600+. I'll fetch it.
        });

        // Actually, just calling the backend chat API or reusing the input field.
        // Let's reuse the input field logic for simplicity.
        // But better to call API directly if possible.
        // Let's simulate input.
        const input = document.getElementById('host-input');
        const originalVal = input.value;
        input.value = cmd;
        await sendHostMessage(); // This function will clear input
        // Restore if needed? No, command sent.

        closeLoreModal();

        // Reset button
        const modal = document.getElementById('lore-modal');
        const saveBtn = modal.querySelector('button[onclick="sendTeachCommand()"]');
        saveBtn.setAttribute('onclick', 'saveLoreEntry()');
        saveBtn.innerText = i18n[state.lang].save_btn;

    } catch (e) { console.error(e); }
}


// --- Logs Logic ---
async function refreshLogs() {
    const listEl = document.getElementById('log-session-list');
    listEl.innerHTML = '<div class="text-center text-slate-400 text-sm mt-10"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';

    try {
        const res = await fetch('/api/logs/sessions');
        const sessions = await res.json();
        renderLogSessions(sessions);
    } catch (e) {
        console.error(e);
        listEl.innerHTML = `<div class="text-center text-red-400 text-sm mt-10">Failed to load logs</div>`;
    }
}

function renderLogSessions(sessions) {
    const listEl = document.getElementById('log-session-list');
    listEl.innerHTML = '';

    if (sessions.length === 0) {
        listEl.innerHTML = `<div class="text-center text-slate-400 text-sm mt-10">No history</div>`;
        return;
    }

    sessions.forEach(sess => {
        const el = document.createElement('div');
        el.className = 'group p-3 rounded-lg hover:bg-white dark:hover:bg-slate-700 cursor-pointer transition border border-transparent hover:border-slate-200 dark:hover:border-slate-600 mb-1 relative';
        el.onclick = () => loadLogChat(sess);

        const date = new Date(sess.timestamp).toLocaleString();

        el.innerHTML = `
            <div class="flex justify-between items-start mb-1 pr-6">
                <span class="font-bold text-slate-700 dark:text-slate-200 text-sm">${sess.visitor_name}</span>
                <span class="text-[10px] text-slate-400">${date}</span>
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400 truncate pr-6">${sess.preview}</div>
            
            <button onclick="deleteLogSession(event, '${sess.session_id}')" 
                class="absolute right-2 top-2 p-1.5 text-slate-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity">
                <i class="fas fa-trash-alt"></i>
            </button>
        `;
        listEl.appendChild(el);
    });
}

async function deleteLogSession(e, sessionId) {
    e.stopPropagation(); // Prevent loading chat
    if (!confirm(i18n[state.lang].confirm_delete_session)) return;

    try {
        await fetch(`/api/logs/sessions/${sessionId}`, { method: 'DELETE' });

        // If current viewing is this one, clear view
        if (currentSessionId === sessionId) {
            document.getElementById('log-chat-container').innerHTML = `<div class="flex h-full items-center justify-center text-slate-400"><span data-i18n="select_session">${i18n[state.lang].select_session}</span></div>`;
            document.getElementById('log-chat-header').classList.add('hidden');
            currentSessionId = null;
        }
        refreshLogs();
    } catch (e) {
        console.error(e);
        alert("Delete failed");
    }
}

let currentSessionId = null;

async function loadLogChat(sessionData) {
    currentSessionId = sessionData.session_id;

    // UI Update (Header)
    document.getElementById('log-chat-header').classList.remove('hidden');
    document.getElementById('log-visitor-name').textContent = sessionData.visitor_name;
    document.getElementById('log-timestamp').textContent = new Date(sessionData.timestamp).toLocaleString();

    const container = document.getElementById('log-chat-container');
    container.innerHTML = '<div class="flex h-full items-center justify-center text-slate-400"><i class="fas fa-spinner fa-spin"></i></div>';

    try {
        const res = await fetch(`/api/logs/messages/${sessionData.session_id}`);
        const messages = await res.json();
        renderLogMessages(messages);
    } catch (e) {
        console.error(e);
        container.innerHTML = `<div class="text-center text-red-400 text-sm mt-10">Failed to load messages</div>`;
    }
}

function renderLogMessages(messages) {
    const container = document.getElementById('log-chat-container');
    container.innerHTML = '';

    // Sort by timestamp just in case
    // messages.sort((a,b) => new Date(a.timestamp) - new Date(b.timestamp));

    messages.forEach(msg => {
        const isHost = msg.sender === 'host';
        const alignClass = isHost ? 'justify-end' : 'justify-start';
        const bubbleClass = isHost
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-600 rounded-bl-none';

        const div = document.createElement('div');
        div.className = `flex ${alignClass}`;
        div.innerHTML = `
            <div class="max-w-[80%] ${bubbleClass} px-4 py-2 rounded-2xl shadow-sm text-sm whitespace-pre-wrap leading-relaxed">
                ${msg.message}
            </div>
        `;
        container.appendChild(div);
    });

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

async function clearAllLogs() {
    if (!confirm(i18n[state.lang].confirm_delete)) return;

    try {
        await fetch('/api/logs', { method: 'DELETE' });
        alert(i18n[state.lang].log_deleted);
        refreshLogs();
        // Clear chat view
        document.getElementById('log-chat-container').innerHTML = `<div class="flex h-full items-center justify-center text-slate-400"><span data-i18n="select_session">${i18n[state.lang].select_session}</span></div>`;
        document.getElementById('log-chat-header').classList.add('hidden');
    } catch (e) {
        console.error(e);
        alert("Error deleting logs");
    }
}

// --- Init ---
document.getElementById('lang-select').addEventListener('change', (e) => updateTexts(e.target.value));
document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
document.getElementById('save-btn').addEventListener('click', saveConfig);
document.getElementById('refresh-rooms').addEventListener('click', fetchRooms);
// document.getElementById('host-chat-form').addEventListener('submit', sendHostMessage);

(async function init() {
    // Restore theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') toggleTheme();

    await loadConfig();
    await fetchRoomStatus();

    // Initial Tab
    switchTab('dashboard');
})();
