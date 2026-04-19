// User ID setup
let userId = localStorage.getItem('lpu_hunt_uid');
if (!userId) {
    userId = 'user_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('lpu_hunt_uid', userId);
}

// UI Elements
const chatbotSidebar = document.getElementById('chatbot-sidebar');
const toggleChatbotBtn = document.getElementById('toggle-chatbot');
const closeChatbotBtn = document.getElementById('close-chatbot');
const chatContents = document.getElementById('chat-contents');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const successOverlay = document.getElementById('success-overlay');
const completionOverlay = document.getElementById('completion-overlay');
const continueBtn = document.getElementById('continue-btn');
const resetBtn = document.getElementById('reset-btn');

// Initialize Map
const lpuCenter = [31.2505, 75.7015];
const map = L.map('map', { zoomControl: false }).setView(lpuCenter, 16);
L.control.zoom({ position: 'bottomleft' }).addTo(map);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);

// Sidebar Toggle Logic
function openChatbot() { chatbotSidebar.className = 'chatbot-visible'; }
function closeChatbot() { chatbotSidebar.className = 'chatbot-hidden'; }
toggleChatbotBtn.addEventListener('click', () => {
    chatbotSidebar.classList.contains('chatbot-hidden') ? openChatbot() : closeChatbot();
});
closeChatbotBtn.addEventListener('click', closeChatbot);

// Map Data Logic
let markers = [];

async function loadMapData() {
    const res = await fetch('/map_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    });
    const data = await res.json();
    
    if (data.completed) {
        completionOverlay.classList.remove('hidden');
    }
    
    // Clear old markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    
    data.locations.forEach(loc => {
        let iconClass = 'pin-locked';
        let iconContent = '<i class="fa-solid fa-lock"></i>';
        
        if (loc.status === 'solved') {
            iconClass = 'pin-solved';
            iconContent = '<i class="fa-solid fa-check"></i>';
        } else if (loc.status === 'active') {
            iconClass = 'pin-active';
            iconContent = '<i class="fa-solid fa-star"></i>';
        }
        
        const customIcon = L.divIcon({
            className: `custom-pin ${iconClass}`,
            html: iconContent,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        const marker = L.marker([loc.lat, loc.lng], { icon: customIcon }).addTo(map);
        markers.push(marker);
        
        if (loc.status === 'active') {
            // Add popup for guessing
            const popupHtml = `
                <div class="popup-content" id="popup-${loc.id}">
                    <h3>Current Target</h3>
                    <p><b>Riddle:</b> ${loc.question}</p>
                    <input type="text" id="guess-${loc.id}" placeholder="Your answer..." autocomplete="off">
                    <button onclick="submitGuess('${loc.id}')">Submit</button>
                    <div id="error-${loc.id}" style="color: #ff4444; margin-top: 5px; font-size: 0.8rem;"></div>
                </div>
            `;
            marker.bindPopup(popupHtml, { closeButton: false, offset: [0, -10] });
            
            // Automatically open if it's active
            setTimeout(() => marker.openPopup(), 500);
            
            // Pan to it
            map.flyTo([loc.lat, loc.lng], 17, { duration: 1.5 });
        } else if (loc.status === 'solved') {
            marker.bindTooltip(`<b>${loc.name}</b><br>(Solved)`, { direction: 'top', offset: [0, -15] });
        }
    });
}

// Guessing Logic
window.submitGuess = async function(locationId) {
    const inputField = document.getElementById(`guess-${locationId}`);
    const errorField = document.getElementById(`error-${locationId}`);
    const answer = inputField.value;
    
    if (!answer) return;
    
    const res = await fetch('/guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, location_id: locationId, answer: answer })
    });
    
    const data = await res.json();
    
    if (data.success) {
        map.closePopup();
        successOverlay.classList.remove('hidden');
    } else {
        errorField.innerText = data.error || "Incorrect!";
        const popupDiv = document.getElementById(`popup-${locationId}`);
        popupDiv.classList.remove('error-shake');
        void popupDiv.offsetWidth; // trigger reflow
        popupDiv.classList.add('error-shake');
        
        if (data.trigger_hint) {
            openChatbot();
            sendMessage("/hint", true);
        }
    }
};

continueBtn.addEventListener('click', () => {
    successOverlay.classList.add('hidden');
    loadMapData();
});

// Chatbot Logic
function scrollToBottom() { chatContents.scrollTop = chatContents.scrollHeight; }

function appendMessage(sender, htmlContent) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'bot' ? 'bot-message' : 'user-message');
    msgDiv.innerHTML = `<div class="message-bubble">${htmlContent}</div>`;
    chatContents.appendChild(msgDiv);
    scrollToBottom();
}

async function sendMessage(message, isSystemTriggered = false) {
    appendMessage('user', isSystemTriggered ? "<i>(Requested hint automatically)</i>" : message);
    userInput.value = '';
    
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.classList.add('message', 'bot-message');
    indicator.innerHTML = `<div class="message-bubble typing-indicator-inner"><i class="fa-solid fa-ellipsis"></i></div>`;
    chatContents.appendChild(indicator);
    scrollToBottom();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, message: message })
        });
        const data = await response.json();
        
        setTimeout(() => {
            document.getElementById('typing-indicator').remove();
            appendMessage('bot', data.reply);
        }, 500);
    } catch {
        document.getElementById('typing-indicator').remove();
        appendMessage('bot', 'Lost connection to neural net!');
    }
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const msg = userInput.value.trim();
    if (msg) sendMessage(msg);
});

resetBtn.addEventListener('click', () => {
    if(confirm("Are you sure you want to completely restart your journey?")) {
        userId = 'user_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('lpu_hunt_uid', userId);
        location.reload();
    }
});

// Landing Page Logic
const landingPage = document.getElementById('landing-page');
if (landingPage) {
    landingPage.addEventListener('click', () => {
        landingPage.classList.add('fade-out');
        setTimeout(() => {
            landingPage.style.display = 'none';
        }, 800);
    });
}

// Boot
loadMapData();
