// ============================================================================
// DJ AI - Frontend Application Logic
// WebSocket + REST API Integration
// ============================================================================

// State
let ws = null;
let reconnectInterval = null;
let currentMode = 'manual';

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat');
const connectionIndicator = document.getElementById('connection-indicator');
const connectionText = document.getElementById('connection-text');

// Mode buttons
const modeBtns = document.querySelectorAll('.mode-btn');
const actionBtns = document.querySelectorAll('.action-btn');

// ============================================================================
// WebSocket Connection
// ============================================================================

function connectWebSocket() {
    const wsUrl = `ws://${window.location.host}/ws`;

    console.log('[WS] Connecting to:', wsUrl);

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('[WS] Connected');
        connectionIndicator.classList.add('connected');
        connectionText.textContent = 'Connected';

        if (reconnectInterval) {
            clearInterval(reconnectInterval);
            reconnectInterval = null;
        }
    };

    ws.onmessage = (event) => {
        try {
            const state = JSON.parse(event.data);
            updateTraktorStatus(state);
        } catch (err) {
            console.error('[WS] Parse error:', err);
        }
    };

    ws.onerror = (error) => {
        console.error('[WS] Error:', error);
    };

    ws.onclose = () => {
        console.log('[WS] Disconnected');
        connectionIndicator.classList.remove('connected');
        connectionText.textContent = 'Disconnected';

        // Auto-reconnect
        if (!reconnectInterval) {
            reconnectInterval = setInterval(() => {
                console.log('[WS] Attempting to reconnect...');
                connectWebSocket();
            }, 3000);
        }
    };
}

// ============================================================================
// Status Update
// ============================================================================

function updateTraktorStatus(state) {
    // Browser
    const browserStatus = state.browser?.track_highlighted || 'N/A';
    document.getElementById('browser-status').textContent = browserStatus;

    // Deck A
    const deckAState = state.deck_a?.status || '--';
    const deckATrack = state.deck_a?.track_title || '--';
    const deckAPlaying = state.deck_a?.playing !== undefined
        ? (state.deck_a.playing ? '▶️ Yes' : '⏸ No')
        : '--';

    document.getElementById('deck-a-state').textContent = deckAState;
    document.getElementById('deck-a-track').textContent = deckATrack;
    document.getElementById('deck-a-playing').innerHTML = deckAPlaying;

    // Deck B
    const deckBState = state.deck_b?.status || '--';
    const deckBTrack = state.deck_b?.track_title || '--';
    const deckBPlaying = state.deck_b?.playing !== undefined
        ? (state.deck_b.playing ? '▶️ Yes' : '⏸ No')
        : '--';

    document.getElementById('deck-b-state').textContent = deckBState;
    document.getElementById('deck-b-track').textContent = deckBTrack;
    document.getElementById('deck-b-playing').innerHTML = deckBPlaying;
}

// ============================================================================
// Chat Functions
// ============================================================================

function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = isUser ? '👤' : '🎧';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Parse content (support markdown-like formatting)
    const formattedContent = formatMessage(content);
    contentDiv.innerHTML = formattedContent;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(text) {
    // Convert line breaks
    let formatted = text.replace(/\n/g, '<br>');

    // Bold text (** or __)
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');

    // Wrap in paragraph if not already HTML
    if (!formatted.includes('<')) {
        formatted = `<p>${formatted}</p>`;
    }

    return formatted;
}

async function sendMessage() {
    const message = chatInput.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessage(message, true);

    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Disable send button
    sendBtn.disabled = true;

    try {
        // Send to API
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: message }),
        });

        const result = await response.json();

        // Add assistant response
        addMessage(result.response, false);

    } catch (error) {
        console.error('[API] Error:', error);
        addMessage('❌ Errore di connessione al server. Riprova.', false);
    } finally {
        // Re-enable send button
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

function clearChat() {
    // Keep only welcome message
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach((msg, index) => {
        if (index > 0) {  // Keep first message (welcome)
            msg.remove();
        }
    });
}

// ============================================================================
// Mode Selection
// ============================================================================

modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;

        // Update UI
        modeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        currentMode = mode;

        // Send mode change to backend
        const modeMessage = `Imposta modalità: ${mode}`;
        addMessage(modeMessage, true);
        sendCommand(modeMessage);
    });
});

// ============================================================================
// Quick Actions
// ============================================================================

actionBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const command = btn.dataset.command;
        chatInput.value = command;
        sendMessage();
    });
});

async function sendCommand(command) {
    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command }),
        });

        const result = await response.json();
        addMessage(result.response, false);

    } catch (error) {
        console.error('[API] Error:', error);
    }
}

// ============================================================================
// Event Listeners
// ============================================================================

// Send button
sendBtn.addEventListener('click', sendMessage);

// Enter key (Shift+Enter for new line)
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea
chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = chatInput.scrollHeight + 'px';
});

// Clear chat
clearChatBtn.addEventListener('click', clearChat);

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('[APP] Initializing DJ AI...');

    // Connect WebSocket
    connectWebSocket();

    // Focus input
    chatInput.focus();

    console.log('[APP] Ready!');
});

// ============================================================================
// Utility Functions
// ============================================================================

function showNotification(message, type = 'info') {
    // TODO: Implement toast notifications
    console.log(`[${type.toUpperCase()}]`, message);
}

// Export for debugging
window.djApp = {
    sendMessage,
    clearChat,
    connectWebSocket,
    state: {
        get mode() { return currentMode; },
        get connected() { return ws && ws.readyState === WebSocket.OPEN; }
    }
};
