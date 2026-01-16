/**
 * Character Card Import/Export Module
 * Handles SillyTavern/Chub V2 format PNG character cards
 */

(function () {
    'use strict';

    // State for the module
    let parsedCardData = null;

    // PNG signature
    const PNG_SIGNATURE = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];

    // CRC32 table for PNG chunk validation
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

    // Initialize modal content on DOM ready
    document.addEventListener('DOMContentLoaded', function () {
        initCharacterCardModal();
    });

    function initCharacterCardModal() {
        const modal = document.getElementById('character-card-modal');
        if (!modal) return;

        modal.innerHTML = `
            <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col transform transition-all scale-100">
                <!-- Header -->
                <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
                    <h3 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
                        <i class="fas fa-id-card text-purple-500"></i>
                        <span data-i18n="character_card_title">Character Card</span>
                    </h3>
                    <button onclick="closeCharacterCardModal()" class="text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>

                <!-- Body -->
                <div class="flex-1 overflow-y-auto p-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- Import Section -->
                        <div class="bg-slate-100 dark:bg-slate-700/30 rounded-lg p-4">
                            <h4 class="font-bold text-slate-700 dark:text-slate-200 mb-3 flex items-center gap-2">
                                <i class="fas fa-file-import text-blue-500"></i>
                                <span data-i18n="card_import">Import</span>
                            </h4>
                            <div id="drop-zone"
                                class="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-500/5 transition-all">
                                <i class="fas fa-cloud-upload-alt text-4xl text-slate-400 mb-3"></i>
                                <p class="text-slate-600 dark:text-slate-300 text-sm" data-i18n="drop_zone_text">
                                    Drag & Drop PNG here<br>or click to select
                                </p>
                                <input type="file" id="card-file-input" accept=".png" class="hidden">
                            </div>
                            <p class="text-xs text-slate-500 mt-2" data-i18n="card_format_hint">
                                Supports SillyTavern/Chub V2 format
                            </p>
                        </div>

                        <!-- Export Section -->
                        <div class="bg-slate-100 dark:bg-slate-700/30 rounded-lg p-4">
                            <h4 class="font-bold text-slate-700 dark:text-slate-200 mb-3 flex items-center gap-2">
                                <i class="fas fa-file-export text-green-500"></i>
                                <span data-i18n="card_export">Export</span>
                            </h4>
                            <p class="text-sm text-slate-600 dark:text-slate-300 mb-4" data-i18n="export_desc">
                                Export current character settings as a PNG character card.
                            </p>
                            <button onclick="exportCharacterCard()"
                                class="w-full py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-bold transition flex items-center justify-center gap-2">
                                <i class="fas fa-download"></i>
                                <span data-i18n="export_btn">Export PNG</span>
                            </button>
                        </div>
                    </div>

                    <!-- Preview Section -->
                    <div id="card-preview" class="hidden mt-6 bg-slate-100 dark:bg-slate-700/30 rounded-lg p-4">
                        <h4 class="font-bold text-slate-700 dark:text-slate-200 mb-3 flex items-center gap-2">
                            <i class="fas fa-eye text-purple-500"></i>
                            <span data-i18n="card_preview">Preview</span>
                        </h4>
                        <div class="space-y-3">
                            <div>
                                <label class="text-xs font-bold text-slate-500" data-i18n="preview_name">Name</label>
                                <p id="preview-name" class="text-slate-800 dark:text-white font-semibold">-</p>
                            </div>
                            <div>
                                <label class="text-xs font-bold text-slate-500" data-i18n="preview_persona">Description / Persona</label>
                                <p id="preview-persona" class="text-slate-700 dark:text-slate-300 text-sm whitespace-pre-wrap max-h-32 overflow-y-auto">-</p>
                            </div>
                            <div>
                                <label class="text-xs font-bold text-slate-500" data-i18n="preview_system">System Prompt</label>
                                <p id="preview-system" class="text-slate-700 dark:text-slate-300 text-sm whitespace-pre-wrap max-h-32 overflow-y-auto">-</p>
                            </div>
                        </div>
                        <button onclick="applyImportedCard()"
                            class="mt-4 w-full py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-bold transition flex items-center justify-center gap-2">
                            <i class="fas fa-check"></i>
                            <span data-i18n="apply_import">Apply Import</span>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Set up event listeners
        setupDropZone();

        // Update i18n if available
        if (typeof updateTexts === 'function') {
            // Try to get current language from global state or DOM
            let currentLang = 'en';
            if (typeof state !== 'undefined' && state.lang) {
                currentLang = state.lang;
            } else {
                const sel = document.getElementById('lang-select');
                if (sel) currentLang = sel.value;
            }
            updateTexts(currentLang);
        }
    }

    function setupDropZone() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('card-file-input');
        if (!dropZone || !fileInput) return;

        // Click to select file
        dropZone.addEventListener('click', () => fileInput.click());

        // File selected
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        // Drag and drop events
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-blue-500', 'bg-blue-500/10');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500', 'bg-blue-500/10');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500', 'bg-blue-500/10');
            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    async function handleFile(file) {
        if (!file.type.includes('png')) {
            alert('Please select a PNG file.');
            return;
        }

        try {
            const arrayBuffer = await file.arrayBuffer();
            const cardData = extractCharacterData(arrayBuffer);

            if (cardData) {
                parsedCardData = cardData;
                showPreview(cardData);
            } else {
                alert('No character data found in this PNG file.');
            }
        } catch (error) {
            console.error('Error reading file:', error);
            alert('Error reading file: ' + error.message);
        }
    }

    function extractCharacterData(arrayBuffer) {
        const data = new Uint8Array(arrayBuffer);

        // Verify PNG signature
        for (let i = 0; i < PNG_SIGNATURE.length; i++) {
            if (data[i] !== PNG_SIGNATURE[i]) {
                throw new Error('Invalid PNG file');
            }
        }

        // Parse chunks
        let offset = 8; // Skip signature
        while (offset < data.length) {
            const length = (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3];
            const type = String.fromCharCode(data[offset + 4], data[offset + 5], data[offset + 6], data[offset + 7]);

            if (type === 'tEXt') {
                const chunkData = data.slice(offset + 8, offset + 8 + length);
                const { keyword, text } = parseTextChunk(chunkData);

                if (keyword === 'chara') {
                    // Decode base64
                    const jsonStr = atob(text);
                    return JSON.parse(jsonStr);
                }
            }

            // Move to next chunk (length + type + data + crc)
            offset += 4 + 4 + length + 4;

            if (type === 'IEND') break;
        }

        return null;
    }

    function parseTextChunk(data) {
        let nullIndex = 0;
        while (nullIndex < data.length && data[nullIndex] !== 0) {
            nullIndex++;
        }

        const keyword = String.fromCharCode(...data.slice(0, nullIndex));
        const text = String.fromCharCode(...data.slice(nullIndex + 1));

        return { keyword, text };
    }

    function showPreview(cardData) {
        const preview = document.getElementById('card-preview');
        if (!preview) return;

        const data = cardData.data || cardData;

        // Build persona from description + personality
        let persona = data.description || '';
        if (data.personality) {
            persona += (persona ? '\n\n' : '') + data.personality;
        }

        document.getElementById('preview-name').textContent = data.name || '-';
        document.getElementById('preview-persona').textContent = persona || '-';
        document.getElementById('preview-system').textContent = data.system_prompt || '-';

        preview.classList.remove('hidden');
    }

    function applyImportedCard() {
        if (!parsedCardData) return;

        const data = parsedCardData.data || parsedCardData;

        // Apply to form fields
        const nameInput = document.getElementById('char-name');
        const personaInput = document.getElementById('char-persona');
        const promptInput = document.getElementById('char-prompt');

        if (nameInput && data.name) {
            nameInput.value = data.name;
        }

        if (personaInput) {
            let persona = data.description || '';
            if (data.personality) {
                persona += (persona ? '\n\n' : '') + data.personality;
            }
            personaInput.value = persona;
        }

        if (promptInput && data.system_prompt) {
            promptInput.value = data.system_prompt;
        }

        // Close modal
        closeCharacterCardModal();

        // Show success message
        alert('Character card imported successfully!');
    }

    async function exportCharacterCard() {
        // Get current values
        const name = document.getElementById('char-name')?.value || 'Character';
        const persona = document.getElementById('char-persona')?.value || '';
        const systemPrompt = document.getElementById('char-prompt')?.value || '';

        // Build V2 spec JSON
        const cardData = {
            spec: 'chara_card_v2',
            spec_version: '2.0',
            data: {
                name: name,
                description: persona,
                personality: '',
                scenario: '',
                first_mes: '',
                mes_example: '',
                creator_notes: 'Exported from roomVerse',
                system_prompt: systemPrompt,
                post_history_instructions: '',
                tags: [],
                creator: 'roomVerse',
                character_version: '1.0',
                extensions: {}
            }
        };

        // Create PNG with embedded data
        const pngBlob = await createCharacterCardPNG(cardData, name);

        // Download
        const url = URL.createObjectURL(pngBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${name.replace(/[^a-zA-Z0-9]/g, '_')}_card.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    async function createCharacterCardPNG(cardData, name) {
        // Create a canvas with character card design
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = 400;
        canvas.height = 600;

        // Background gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, '#6366f1');
        gradient.addColorStop(1, '#8b5cf6');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Card frame
        ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.roundRect(20, 20, canvas.width - 40, canvas.height - 40, 20);
        ctx.fill();

        // Character icon placeholder
        ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.beginPath();
        ctx.arc(canvas.width / 2, 180, 80, 0, Math.PI * 2);
        ctx.fill();

        // Icon
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.font = '60px FontAwesome';
        ctx.textAlign = 'center';
        ctx.fillText('\uf007', canvas.width / 2, 200);

        // Name
        ctx.fillStyle = 'white';
        ctx.font = 'bold 28px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(name, canvas.width / 2, 320);

        // Subtitle
        ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.font = '14px Inter, sans-serif';
        ctx.fillText('roomVerse Character Card', canvas.width / 2, 350);

        // Decorative line
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(80, 380);
        ctx.lineTo(canvas.width - 80, 380);
        ctx.stroke();

        // Footer text
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.font = '12px Inter, sans-serif';
        ctx.fillText('SillyTavern V2 Compatible', canvas.width / 2, canvas.height - 40);

        // Get PNG data
        const pngDataUrl = canvas.toDataURL('image/png');
        const pngBase64 = pngDataUrl.split(',')[1];
        const pngData = Uint8Array.from(atob(pngBase64), c => c.charCodeAt(0));

        // Inject character data as tEXt chunk
        const jsonStr = JSON.stringify(cardData);
        const base64Data = btoa(jsonStr);
        const pngWithData = injectTextChunk(pngData, 'chara', base64Data);

        return new Blob([pngWithData], { type: 'image/png' });
    }

    function injectTextChunk(pngData, keyword, text) {
        // Find IEND chunk position
        let iendPos = -1;
        let offset = 8;

        while (offset < pngData.length) {
            const length = (pngData[offset] << 24) | (pngData[offset + 1] << 16) | (pngData[offset + 2] << 8) | pngData[offset + 3];
            const type = String.fromCharCode(pngData[offset + 4], pngData[offset + 5], pngData[offset + 6], pngData[offset + 7]);

            if (type === 'IEND') {
                iendPos = offset;
                break;
            }

            offset += 4 + 4 + length + 4;
        }

        if (iendPos === -1) {
            throw new Error('Invalid PNG: IEND chunk not found');
        }

        // Create tEXt chunk
        const keywordBytes = new TextEncoder().encode(keyword);
        const textBytes = new TextEncoder().encode(text);
        const chunkData = new Uint8Array(keywordBytes.length + 1 + textBytes.length);
        chunkData.set(keywordBytes, 0);
        chunkData[keywordBytes.length] = 0; // Null separator
        chunkData.set(textBytes, keywordBytes.length + 1);

        // Build chunk: length (4) + type (4) + data + crc (4)
        const chunkType = new TextEncoder().encode('tEXt');
        const chunkLength = chunkData.length;

        // Calculate CRC (type + data)
        const crcInput = new Uint8Array(4 + chunkData.length);
        crcInput.set(chunkType, 0);
        crcInput.set(chunkData, 4);
        const crcValue = crc32(crcInput);

        // Build full chunk
        const chunk = new Uint8Array(4 + 4 + chunkData.length + 4);
        chunk[0] = (chunkLength >> 24) & 0xFF;
        chunk[1] = (chunkLength >> 16) & 0xFF;
        chunk[2] = (chunkLength >> 8) & 0xFF;
        chunk[3] = chunkLength & 0xFF;
        chunk.set(chunkType, 4);
        chunk.set(chunkData, 8);
        chunk[chunk.length - 4] = (crcValue >> 24) & 0xFF;
        chunk[chunk.length - 3] = (crcValue >> 16) & 0xFF;
        chunk[chunk.length - 2] = (crcValue >> 8) & 0xFF;
        chunk[chunk.length - 1] = crcValue & 0xFF;

        // Combine: before IEND + new chunk + IEND
        const result = new Uint8Array(pngData.length + chunk.length);
        result.set(pngData.slice(0, iendPos), 0);
        result.set(chunk, iendPos);
        result.set(pngData.slice(iendPos), iendPos + chunk.length);
        return result;
    }

    // Global functions
    window.openCharacterCardModal = function () {
        console.log('[CharCard] openCharacterCardModal called');
        const modal = document.getElementById('character-card-modal');
        if (modal) {
            modal.classList.remove('hidden');
            // Reset preview
            document.getElementById('card-preview')?.classList.add('hidden');
            parsedCardData = null;

            // Force update i18n
            console.log('[CharCard] Checking for updateTexts function...');
            if (typeof window.updateTexts === 'function') {
                let currentLang = 'en';
                // Try reading from DOM first as it is source of truth for UI
                const sel = document.getElementById('lang-select');
                if (sel) {
                    currentLang = sel.value;
                    console.log('[CharCard] Detected lang from dropdown:', currentLang);
                } else if (typeof state !== 'undefined' && state.lang) {
                    currentLang = state.lang;
                    console.log('[CharCard] Detected lang from state:', currentLang);
                }

                console.log('[CharCard] Calling updateTexts with:', currentLang);
                window.updateTexts(currentLang);
            } else {
                console.error('[CharCard] updateTexts function not found!');
            }
        } else {
            console.error('[CharCard] Modal not found!');
        }
    };

    window.closeCharacterCardModal = function () {
        const modal = document.getElementById('character-card-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    };

    window.exportCharacterCard = exportCharacterCard;
    window.applyImportedCard = applyImportedCard;

    // Close modal on backdrop click
    document.addEventListener('click', function (e) {
        const modal = document.getElementById('character-card-modal');
        if (e.target === modal) {
            closeCharacterCardModal();
        }
    });

})();
