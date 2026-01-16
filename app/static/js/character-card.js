/**
 * Character Card Manager Module
 * Handles CRUD, Import/Export/PNG Parsing for Character Cards
 */

(function () {
    'use strict';

    // State
    let cards = [];
    let editingCard = null; // null = create new
    let activeTab = 'library'; // library, editor, import

    // PNG Utils
    const PNG_SIGNATURE = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];
    const crcTable = (function () {
        const table = new Uint32Array(256);
        for (let i = 0; i < 256; i++) {
            let c = i;
            for (let j = 0; j < 8; j++) {
                c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
            }
            table[i] = c;
        }
        return table;
    })();

    function crc32(data) {
        let crc = 0xFFFFFFFF;
        for (let i = 0; i < data.length; i++) {
            crc = crcTable[(crc ^ data[i]) & 0xFF] ^ (crc >>> 8);
        }
        return (crc ^ 0xFFFFFFFF) >>> 0;
    }

    // --- Main Entry ---

    window.openCharacterCardModal = async function () {
        console.log('[CharCard] Opening Manager...');
        const modal = document.getElementById('character-card-modal');
        if (modal) {
            modal.classList.remove('hidden');
            activeTab = 'library';
            await loadCards(); // Fetch from API
            renderModal();
            updateI18n();
        }
    };

    window.closeCharacterCardModal = function () {
        const modal = document.getElementById('character-card-modal');
        if (modal) modal.classList.add('hidden');
    };

    // --- Data Logic (API) ---

    async function loadCards() {
        try {
            const res = await fetch('/api/cards');
            if (res.ok) {
                cards = await res.json();
            } else {
                console.error('Failed to load cards');
            }
        } catch (e) {
            console.error('Error loading cards:', e);
        }
    }

    async function apiSaveCard(cardData) {
        const isUpdate = !!cardData.id;
        const url = isUpdate ? `/api/cards/${cardData.id}` : '/api/cards';
        const method = isUpdate ? 'PUT' : 'POST';

        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cardData)
            });
            return await res.json();
        } catch (e) {
            console.error('Save error:', e);
            throw e;
        }
    }

    async function apiUploadImage(cardId, file) {
        const body = new FormData();
        body.append('file', file);

        try {
            const res = await fetch(`/api/cards/${cardId}/image`, {
                method: 'POST',
                body: body
            });
            return await res.json();
        } catch (e) {
            console.error('Upload Error:', e);
        }
    }

    async function apiDeleteCard(id) {
        await fetch(`/api/cards/${id}`, { method: 'DELETE' });
    }

    async function apiActivateCard(id) {
        await fetch(`/api/cards/${id}/activate`, { method: 'POST' });
        // Update Dashboard UI
        if (window.loadConfig) window.loadConfig();
    }

    // --- Rendering ---

    function renderModal() {
        const modal = document.getElementById('character-card-modal');
        if (!modal) return;

        modal.innerHTML = `
            <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden">
                <!-- Header -->
                <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
                    <h3 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
                        <i class="fas fa-layer-group text-purple-500"></i>
                        <span data-i18n="card_manager_title">Character Cards</span>
                    </h3>
                    <button onclick="closeCharacterCardModal()" class="text-slate-500 hover:text-slate-700 dark:hover:text-slate-300">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>

                <!-- Tabs -->
                <div class="flex border-b border-slate-200 dark:border-slate-700">
                    <button onclick="switchCardTab('library')" class="px-6 py-3 font-medium text-sm transition-colors ${activeTab === 'library' ? 'text-blue-600 border-b-2 border-blue-600 dark:text-blue-400' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400'}">
                        <i class="fas fa-list mr-2"></i> <span data-i18n="tab_library">Library</span>
                    </button>
                    <button onclick="switchCardTab('editor')" class="px-6 py-3 font-medium text-sm transition-colors ${activeTab === 'editor' ? 'text-blue-600 border-b-2 border-blue-600 dark:text-blue-400' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400'}">
                        <i class="fas fa-edit mr-2"></i> <span data-i18n="tab_editor">Editor</span>
                    </button>
                    <button onclick="switchCardTab('import')" class="px-6 py-3 font-medium text-sm transition-colors ${activeTab === 'import' ? 'text-blue-600 border-b-2 border-blue-600 dark:text-blue-400' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400'}">
                        <i class="fas fa-file-import mr-2"></i> <span data-i18n="tab_import">Import (PNG)</span>
                    </button>
                </div>

                <!-- Content -->
                <div class="flex-1 overflow-y-auto p-6 bg-slate-50 dark:bg-slate-900/30">
                    ${getTabContent()}
                </div>
            </div>
        `;

        // Post-render setup
        if (activeTab === 'import') setupDropZone();
        updateI18n();
    }

    function getTabContent() {
        if (activeTab === 'library') return renderLibraryHTML();
        if (activeTab === 'editor') return renderEditorHTML();
        if (activeTab === 'import') return renderImportHTML();
        return '';
    }

    function renderLibraryHTML() {
        if (cards.length === 0) {
            return `
                <div class="text-center py-12 text-slate-500">
                    <i class="fas fa-box-open text-4xl mb-3 opacity-50"></i>
                    <p data-i18n="no_cards">No cards found. Create one or Import!</p>
                    <button onclick="createNewCard()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                        <span data-i18n="create_new">Create New</span>
                    </button>
                </div>
            `;
        }

        const activeId = (window.state && window.state.config && window.state.config.character && window.state.config.character.active_card_id);

        return `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="col-span-1 md:col-span-2 lg:col-span-3 flex justify-end mb-2">
                     <button onclick="createNewCard()" class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm flex items-center gap-2">
                        <i class="fas fa-plus"></i> <span data-i18n="create_add">Add Card</span>
                    </button>
                </div>
                ${cards.map(card => {
            // Decide Avatar URL
            const avatarUrl = card.image_path ?
                `/dashboard/cards/${card.image_path}` :
                null;

            return `
                    <div class="bg-white dark:bg-slate-800 rounded-lg shadow border border-slate-200 dark:border-slate-700 p-4 relative group ${activeId === card.id ? 'ring-2 ring-blue-500' : ''}">
                        ${activeId === card.id ? '<div class="absolute top-2 right-2 text-blue-500"><i class="fas fa-check-circle"></i> Active</div>' : ''}
                        
                        <div class="flex gap-4 mb-3">
                             <!-- Avatar -->
                             <div class="w-16 h-24 bg-slate-200 dark:bg-slate-700 rounded-lg shrink-0 overflow-hidden flex items-center justify-center">
                                 ${avatarUrl ?
                    `<img src="${avatarUrl}" class="w-full h-full object-cover">` :
                    `<i class="fas fa-user text-slate-400 text-2xl"></i>`
                }
                             </div>
                             
                             <div class="flex-1 min-w-0">
                                <h4 class="font-bold text-lg mb-1 truncate">${escape(card.name)}</h4>
                                <p class="text-xs text-slate-500 mb-2 truncate">v${card.character_version || '1.0'} by ${filterXSS(card.creator || 'Unknown')}</p>
                                <div class="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 h-10">
                                    ${filterXSS(card.description || 'No description.')}
                                </div>
                             </div>
                        </div>

                        <div class="flex gap-2 mt-auto">
                            ${activeId !== card.id ? `
                                <button onclick="doActivateCard(${card.id})" class="flex-1 py-1.5 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-sm font-medium dark:bg-blue-900/30 dark:text-blue-300 dark:hover:bg-blue-900/50">
                                    <span data-i18n="btn_activate">Activate</span>
                                </button>
                            ` : `
                                <button onclick="doDeactivateCard()" class="flex-1 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-sm font-medium dark:bg-slate-700 dark:text-slate-300">
                                    <span data-i18n="btn_deactivate">Deactivate</span>
                                </button>
                            `}
                            
                            <button onclick="editCard(${card.id})" class="p-2 text-slate-500 hover:text-blue-500 rounded bg-slate-50 dark:bg-slate-700 hover:bg-blue-50 dark:hover:bg-blue-900/20">
                                <i class="fas fa-edit"></i>
                            </button>
                             <button onclick="doExportCard(${card.id})" class="p-2 text-slate-500 hover:text-green-500 rounded bg-slate-50 dark:bg-slate-700 hover:bg-green-50 dark:hover:bg-green-900/20">
                                <i class="fas fa-download"></i>
                            </button>
                            <button onclick="doDeleteCard(${card.id})" class="p-2 text-slate-500 hover:text-red-500 rounded bg-slate-50 dark:bg-slate-700 hover:bg-red-50 dark:hover:bg-red-900/20">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `}).join('')}
            </div>
        `;
    }

    function renderEditorHTML() {
        const c = editingCard || { name: '', description: '', personality: '', scenario: '', first_mes: '', mes_example: '', system_prompt: '' };
        const avatarUrl = (c && c.image_path) ? `/dashboard/cards/${c.image_path}` : null;

        return `
            <div class="space-y-4 max-w-4xl mx-auto">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Left: Avatar Upload -->
                    <div class="md:col-span-1">
                        <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Avatar Image</label>
                        <div class="w-full aspect-[2/3] bg-slate-200 dark:bg-slate-700 rounded-lg overflow-hidden relative group border-2 border-dashed border-slate-400 dark:border-slate-600 hover:border-blue-500 transition-colors">
                            <img id="avatar-preview" src="${avatarUrl || ''}" class="w-full h-full object-cover ${avatarUrl ? '' : 'hidden'}">
                            <div class="absolute inset-0 flex items-center justify-center pointer-events-none ${avatarUrl ? 'opacity-0 group-hover:opacity-100 bg-black/40 transition-opacity' : ''}">
                                <div class="text-center text-slate-500 dark:text-slate-300 p-2">
                                    <i class="fas fa-camera text-2xl mb-1"></i>
                                    <p class="text-xs">Click to Upload</p>
                                </div>
                            </div>
                            <input type="file" id="edit-avatar" accept="image/png" class="absolute inset-0 opacity-0 cursor-pointer" onchange="previewAvatar(this)">
                        </div>
                        <p class="text-xs text-slate-500 mt-2 text-center">PNG only. Will verify on Save.</p>
                    </div>

                    <!-- Right: Fields -->
                    <div class="md:col-span-2 space-y-4">
                         <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1" data-i18n="label_name">Name</label>
                                <input type="text" id="edit-name" value="${escape(c.name)}" class="w-full rounded border-slate-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white p-2">
                            </div>
                             <div>
                                <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1" data-i18n="label_creator">Creator</label>
                                <input type="text" id="edit-creator" value="${escape(c.creator || '')}" class="w-full rounded border-slate-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white p-2">
                            </div>
                        </div>

                        <div>
                            <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1" data-i18n="label_description">Description</label>
                            <textarea id="edit-description" rows="3" class="w-full rounded border-slate-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white p-2 font-mono text-sm">${escape(c.description || '')}</textarea>
                        </div>

                        <div>
                            <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1" data-i18n="label_personality">Personality</label>
                            <textarea id="edit-personality" rows="3" class="w-full rounded border-slate-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white p-2 font-mono text-sm">${escape(c.personality || '')}</textarea>
                        </div>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                     <div>
                        <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1" data-i18n="label_scenario">Scenario</label>
                        <textarea id="edit-scenario" rows="4" class="w-full rounded border-slate-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white p-2 font-mono text-sm">${escape(c.scenario || '')}</textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1" data-i18n="label_first_mes">First Message</label>
                        <textarea id="edit-first-mes" rows="4" class="w-full rounded border-slate-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white p-2 font-mono text-sm">${escape(c.first_mes || '')}</textarea>
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1" data-i18n="label_mes_example">Message Examples</label>
                    <textarea id="edit-mes-example" rows="4" class="w-full rounded border-slate-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white p-2 font-mono text-sm">${escape(c.mes_example || '')}</textarea>
                </div>
                
                <div>
                     <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1" data-i18n="label_system_prompt">System Prompt (Override/Append)</label>
                     <textarea id="edit-system-prompt" rows="2" class="w-full rounded border-slate-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white p-2 font-mono text-sm">${escape(c.system_prompt || '')}</textarea>
                </div>

                <div class="flex justify-end gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
                    <button onclick="switchCardTab('library')" class="px-4 py-2 text-slate-600 hover:text-slate-800 dark:text-slate-400 dark:hover:text-white">Cancel</button>
                    <button onclick="doSaveCard()" class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-bold">
                        <span data-i18n="btn_save_card">Save Card</span>
                    </button>
                </div>
            </div>
        `;
    }

    function renderImportHTML() {
        return `
            <div class="max-w-2xl mx-auto py-8">
                <div id="drop-zone"
                    class="border-4 border-dashed border-slate-300 dark:border-slate-600 rounded-2xl p-12 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-500/5 transition-all">
                    <i class="fas fa-cloud-upload-alt text-6xl text-slate-400 mb-6"></i>
                    <h3 class="text-xl font-bold text-slate-700 dark:text-slate-200 mb-2">
                        Drag & Drop Character Card (PNG)
                    </h3>
                    <p class="text-slate-500 dark:text-slate-400 mb-6">SillyTavern / Chub V2 Format</p>
                    <input type="file" id="card-file-input" accept=".png" class="hidden">
                    <button class="px-6 py-2 bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 font-medium">
                        Select File
                    </button>
                </div>
            </div>
        `;
    }

    // --- Actions ---

    window.switchCardTab = function (tab) {
        activeTab = tab;
        if (tab === 'library') loadCards().then(renderModal);
        else renderModal();
    };

    window.createNewCard = function () {
        editingCard = null;
        activeTab = 'editor';
        renderModal();
    };

    window.editCard = function (id) {
        editingCard = cards.find(c => c.id === id);
        activeTab = 'editor';
        renderModal();
    };

    window.previewAvatar = function (input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = document.getElementById('avatar-preview');
                img.src = e.target.result;
                img.classList.remove('hidden');
            };
            reader.readAsDataURL(input.files[0]);
        }
    };

    window.doSaveCard = async function () {
        const data = {
            id: editingCard ? editingCard.id : undefined,
            name: document.getElementById('edit-name').value,
            creator: document.getElementById('edit-creator').value,
            description: document.getElementById('edit-description').value,
            personality: document.getElementById('edit-personality').value,
            scenario: document.getElementById('edit-scenario').value,
            first_mes: document.getElementById('edit-first-mes').value,
            mes_example: document.getElementById('edit-mes-example').value,
            system_prompt: document.getElementById('edit-system-prompt').value,
        };

        if (!data.name) return alert('Name is required');

        // 1. Save Data
        const savedCard = await apiSaveCard(data);

        // 2. Upload Image if present
        const fileInput = document.getElementById('edit-avatar');
        if (fileInput && fileInput.files.length > 0) {
            await apiUploadImage(savedCard.id, fileInput.files[0]);
        }

        activeTab = 'library';
        await loadCards();
        renderModal();
    };

    window.doDeleteCard = async function (id) {
        if (!confirm('Delete this card?')) return;
        await apiDeleteCard(id);
        await loadCards();
        renderModal();
    };

    window.doActivateCard = async function (id) {
        await apiActivateCard(id);
        await loadCards();
        renderModal();
    };

    window.doDeactivateCard = async function () {
        await fetch('/api/cards/deactivate', { method: 'POST' });
        if (window.loadConfig) window.loadConfig();
        await loadCards();
        renderModal();
    };

    window.doExportCard = async function (id) {
        const card = cards.find(c => c.id === id);
        if (!card) return;

        const cardData = {
            spec: 'chara_card_v2',
            spec_version: '2.0',
            data: {
                name: card.name,
                description: card.description || '',
                personality: card.personality || '',
                scenario: card.scenario || '',
                first_mes: card.first_mes || '',
                mes_example: card.mes_example || '',
                creator_notes: card.creator_notes || '',
                system_prompt: card.system_prompt || '',
                creator: card.creator || 'RoomVerse',
                character_version: card.character_version || '1.0',
                tags: []
            }
        };

        // Reuse image if available
        if (card.image_path) {
            try {
                const resp = await fetch(`/dashboard/cards/${card.image_path}`);
                const blob = await resp.blob();
                const buffer = await blob.arrayBuffer();

                // Inject chunks into this Custom Image
                const pngData = new Uint8Array(buffer);
                const jsonStr = JSON.stringify(cardData);
                const b64 = btoa(jsonStr);

                const injected = injectTextChunk(pngData, 'chara', b64);
                const finalBlob = new Blob([injected], { type: 'image/png' });
                downloadBlob(finalBlob, `${card.name.replace(/[^a-z0-9]/gi, '_')}.png`);
                return;

            } catch (e) {
                console.error("Failed to load custom avatar for export, fallback to default", e);
            }
        }

        // Fallback: Generate Default
        const pngBlob = await createCharacterCardPNG(cardData, card.name);
        downloadBlob(pngBlob, `${card.name.replace(/[^a-z0-9]/gi, '_')}.png`);
    };

    // --- Import Logic ---

    function setupDropZone() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('card-file-input');
        if (!dropZone || !fileInput) return;

        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleFile(e.target.files[0]);
        });

        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('border-blue-500'); });
        dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); dropZone.classList.remove('border-blue-500'); });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500');
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });
    }

    async function handleFile(file) {
        if (!file.type.includes('png')) return alert('Use PNG');
        try {
            const buff = await file.arrayBuffer();
            const json = extractCharacterData(buff);
            if (!json) throw new Error("No card data");

            // Convert to DB format
            const d = json.data || json;
            const newCard = {
                name: d.name || 'Imported',
                description: d.description,
                personality: d.personality,
                scenario: d.scenario,
                first_mes: d.first_mes,
                mes_example: d.mes_example,
                system_prompt: d.system_prompt,
                creator: d.creator,
                character_version: d.character_version,
                creator_notes: d.creator_notes
            };

            const saved = await apiSaveCard(newCard);

            // Re-upload the Imported PNG as the Avatar!
            // We need to send 'file' to apiUploadImage
            await apiUploadImage(saved.id, file);

            alert('Card Imported!');
            activeTab = 'library';
            await loadCards(); // ensure we have the new ID
            renderModal();

        } catch (e) {
            alert('Error: ' + e.message);
        }
    }

    // --- Helpers ---

    function escape(str) {
        if (!str) return '';
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    function filterXSS(str) {
        return escape(str);
    }

    function downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function updateI18n() {
        if (window.updateTexts && typeof window.updateTexts === 'function') {
            // Re-detect lang
            const sel = document.getElementById('lang-select');
            let lang = 'en';
            if (sel) lang = sel.value;
            else if (window.state && window.state.lang) lang = window.state.lang;

            window.updateTexts(lang);
        }
    }


    // --- PNG Core (Reuse existing logic) ---
    // (Collapsed for brevity, but needed)

    // ... [Copy paste extractCharacterData, parseTextChunk, createCharacterCardPNG, injectTextChunk from before] ...
    // Since I am rewriting the whole file, I MUST include them.

    function extractCharacterData(arrayBuffer) {
        const data = new Uint8Array(arrayBuffer);
        for (let i = 0; i < PNG_SIGNATURE.length; i++) {
            if (data[i] !== PNG_SIGNATURE[i]) throw new Error('Invalid PNG file');
        }
        let offset = 8;
        while (offset < data.length) {
            const length = (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3];
            const type = String.fromCharCode(data[offset + 4], data[offset + 5], data[offset + 6], data[offset + 7]);
            if (type === 'tEXt') {
                const chunkData = data.slice(offset + 8, offset + 8 + length);
                let nullIndex = 0;
                while (nullIndex < chunkData.length && chunkData[nullIndex] !== 0) nullIndex++;
                const key = String.fromCharCode(...chunkData.slice(0, nullIndex));
                const text = String.fromCharCode(...chunkData.slice(nullIndex + 1));
                if (key === 'chara') return JSON.parse(atob(text));
            }
            offset += 4 + 4 + length + 4;
            if (type === 'IEND') break;
        }
        return null;
    }

    async function createCharacterCardPNG(cardData, name) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 400; canvas.height = 600;

        // Gradient
        const g = ctx.createLinearGradient(0, 0, 0, 600);
        g.addColorStop(0, '#6366f1'); g.addColorStop(1, '#8b5cf6');
        ctx.fillStyle = g; ctx.fillRect(0, 0, 400, 600);

        ctx.fillStyle = 'white';
        ctx.font = 'bold 28px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(name, 200, 300);

        ctx.font = '14px sans-serif';
        ctx.fillText('RoomVerse Card', 200, 330);

        const pngUrl = canvas.toDataURL('image/png');
        const pngData = Uint8Array.from(atob(pngUrl.split(',')[1]), c => c.charCodeAt(0));

        const jsonStr = JSON.stringify(cardData);
        const b64 = btoa(jsonStr);
        return new Blob([injectTextChunk(pngData, 'chara', b64)], { type: 'image/png' });
    }

    function injectTextChunk(pngData, keyword, text) {
        let iend = -1;
        let offset = 8;
        while (offset < pngData.length) {
            const len = (pngData[offset] << 24) | (pngData[offset + 1] << 16) | (pngData[offset + 2] << 8) | pngData[offset + 3];
            const type = String.fromCharCode(pngData[offset + 4], pngData[offset + 5], pngData[offset + 6], pngData[offset + 7]);
            if (type === 'IEND') { iend = offset; break; }
            offset += 12 + len;
        }

        const kBytes = new TextEncoder().encode(keyword);
        const tBytes = new TextEncoder().encode(text);
        const data = new Uint8Array(kBytes.length + 1 + tBytes.length);
        data.set(kBytes, 0); data[kBytes.length] = 0; data.set(tBytes, kBytes.length + 1);

        const type = new TextEncoder().encode('tEXt');
        const crcIn = new Uint8Array(4 + data.length);
        crcIn.set(type, 0); crcIn.set(data, 4);
        const crc = crc32(crcIn);

        const chunk = new Uint8Array(12 + data.length);
        const len = data.length;
        chunk[0] = len >> 24; chunk[1] = len >> 16; chunk[2] = len >> 8; chunk[3] = len;
        chunk.set(type, 4); chunk.set(data, 8);
        chunk[chunk.length - 4] = crc >> 24; chunk[chunk.length - 3] = crc >> 16; chunk[chunk.length - 2] = crc >> 8; chunk[chunk.length - 1] = crc;

        const res = new Uint8Array(pngData.length + chunk.length);
        res.set(pngData.slice(0, iend), 0);
        res.set(chunk, iend);
        res.set(pngData.slice(iend), iend + chunk.length);
        return res;
    }

})();
