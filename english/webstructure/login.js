(function() {
    'use strict';

    const CONFIG = {
        storageKey: 'studykey_username',
        ipStorageKey: 'studykey_ip',
        loginImageName: 'login.png',
        transitionDelay: 500,
        fadeOutDuration: 800,
    };

    let userIP = null;
    let overlay = null;
    let loginBox = null;
    let imageContainer = null;
    let loginIcon = null;
    let greetingText = null;
    let nameInput = null;
    let submitBtn = null;
    let loadingDots = null;

    function getScriptDir() {
        const scripts = document.getElementsByTagName('script');
        for (let i = scripts.length - 1; i >= 0; i--) {
            const src = scripts[i].src;
            if (src && src.includes('login.js')) {
                const url = new URL(src);
                const pathParts = url.pathname.split('/');
                pathParts.pop();
                return pathParts.join('/');
            }
        }
        return window.location.pathname.split('/').slice(0, -1).join('/');
    }

    const SCRIPT_DIR = getScriptDir();
    const LOGIN_IMAGE_PATH = SCRIPT_DIR + '/' + CONFIG.loginImageName;

    async function fetchUserIP() {
        try {
            const services = [
                'https://api.ipify.org?format=json',
                'https://api.ip.sb/ip',
                'https://api.my-ip.io/ip'
            ];

            for (const service of services) {
                try {
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 3000);
                    
                    const response = await fetch(service, { signal: controller.signal });
                    clearTimeout(timeoutId);
                    
                    if (response.ok) {
                        const contentType = response.headers.get('content-type');
                        if (contentType && contentType.includes('application/json')) {
                            const data = await response.json();
                            return data.ip || String(data);
                        }
                        const text = await response.text();
                        return text.trim();
                    }
                } catch (e) {
                    continue;
                }
            }
            
            return 'Unknown';
        } catch (error) {
            return 'Unknown';
        }
    }

    function createOverlay() {
        overlay = document.createElement('div');
        overlay.className = 'login-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-label', 'Login');
        
        loginBox = document.createElement('div');
        loginBox.className = 'login-box';
        
        imageContainer = document.createElement('div');
        imageContainer.className = 'login-image-container';
        
        loginIcon = document.createElement('img');
        loginIcon.className = 'login-icon';
        loginIcon.src = LOGIN_IMAGE_PATH;
        loginIcon.alt = 'Study Key Login';
        loginIcon.onerror = function() {
            this.style.display = 'none';
            const placeholder = document.createElement('div');
            placeholder.style.cssText = 'width:160px;height:160px;background:#e8ecf1;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:48px;';
            placeholder.textContent = '📚';
            imageContainer.appendChild(placeholder);
        };
        
        imageContainer.appendChild(loginIcon);
        
        greetingText = document.createElement('div');
        greetingText.className = 'login-greeting';
        greetingText.innerHTML = `
            <p>Hey there! I don't recognize you yet.</p>
            <p>I see you as <span class="ip-display" id="user-ip-display">${userIP || '...'}</span></p>
            <p>What should I call you?</p>
        `;
        
        const inputArea = document.createElement('div');
        inputArea.className = 'login-input-area';
        
        nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.placeholder = 'Enter your name';
        nameInput.maxLength = 30;
        nameInput.autocomplete = 'off';
        nameInput.setAttribute('aria-label', 'Enter your name');
        
        submitBtn = document.createElement('button');
        submitBtn.textContent = 'Continue';
        submitBtn.type = 'button';
        
        loadingDots = document.createElement('div');
        loadingDots.className = 'login-loading-dots';
        loadingDots.innerHTML = `
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        `;
        
        inputArea.appendChild(nameInput);
        inputArea.appendChild(submitBtn);
        inputArea.appendChild(loadingDots);
        
        loginBox.appendChild(imageContainer);
        loginBox.appendChild(greetingText);
        loginBox.appendChild(inputArea);
        overlay.appendChild(loginBox);
        
        document.body.appendChild(overlay);
        
        requestAnimationFrame(() => {
            overlay.classList.add('active');
        });
    }

    function handleSubmit() {
        const name = nameInput.value.trim();
        
        if (!name || name.length < 2) {
            shakeElement(nameInput);
            return;
        }
        
        nameInput.disabled = true;
        submitBtn.disabled = true;
        submitBtn.style.display = 'none';
        loadingDots.classList.add('active');
        
        localStorage.setItem(CONFIG.storageKey, name);
        if (userIP && userIP !== 'Unknown') {
            localStorage.setItem(CONFIG.ipStorageKey, userIP);
        }
        
        setTimeout(() => {
            transitionToSuccess(name);
        }, CONFIG.transitionDelay);
    }

    function handleKeyPress(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleSubmit();
        }
    }

    function transitionToSuccess(name) {
        loadingDots.classList.remove('active');
        loadingDots.style.display = 'none';
        
        nameInput.style.display = 'none';
        submitBtn.style.display = 'none';
        
        loginIcon.classList.add('hidden');
        loginIcon.style.display = 'none';
        
        const animContainer = document.createElement('div');
        animContainer.className = 'faceid-success-container';
        animContainer.innerHTML = `
            <div class="faceid-circle">
                <div class="faceid-ring"></div>
                <div class="faceid-check">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path class="check-path" d="M5 13l4 4L19 7" stroke="#1a56db" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        `;
        
        imageContainer.appendChild(animContainer);
        
        greetingText.innerHTML = `
            <div class="login-welcome">
                <p class="welcome-name">Welcome, ${escapeHTML(name)}!</p>
                <p class="welcome-sub">Login successful</p>
            </div>
        `;
        
        requestAnimationFrame(() => {
            const circle = animContainer.querySelector('.faceid-circle');
            if (circle) {
                circle.classList.add('animate');
            }
        });
        
        setTimeout(() => closeModal(), 2200);
    }

    function closeModal() {
        if (!overlay) return;
        
        overlay.classList.add('fade-out');
        
        setTimeout(() => {
            if (overlay && overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
            overlay = null;
            loginBox = null;
            imageContainer = null;
            loginIcon = null;
            greetingText = null;
            nameInput = null;
            submitBtn = null;
            loadingDots = null;
        }, CONFIG.fadeOutDuration);
    }

    function shakeElement(element) {
        element.style.animation = 'none';
        element.offsetHeight;
        element.style.animation = 'shake 0.5s ease';
        element.style.borderColor = '#ef4444';
        
        setTimeout(() => {
            element.style.borderColor = '';
            element.style.animation = '';
        }, 2000);
    }

    function escapeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    async function init() {
        const storedName = localStorage.getItem(CONFIG.storageKey);
        
        if (storedName) {
            return;
        }
        
        userIP = await fetchUserIP();
        
        createOverlay();
        
        const ipDisplay = document.getElementById('user-ip-display');
        if (ipDisplay) {
            ipDisplay.textContent = userIP || 'Unknown';
        }
        
        submitBtn.addEventListener('click', handleSubmit);
        nameInput.addEventListener('keypress', handleKeyPress);
        
        setTimeout(() => {
            if (nameInput) {
                nameInput.focus();
            }
        }, 600);
    }

    const shakeStyle = document.createElement('style');
    shakeStyle.textContent = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-6px); }
            20%, 40%, 60%, 80% { transform: translateX(6px); }
        }
    `;
    document.head.appendChild(shakeStyle);

    window.StudyKeyLogin = {
        getUserName: function() {
            return localStorage.getItem(CONFIG.storageKey);
        },
        
        getUserIP: function() {
            return localStorage.getItem(CONFIG.ipStorageKey);
        },
        
        logout: function() {
            localStorage.removeItem(CONFIG.storageKey);
            localStorage.removeItem(CONFIG.ipStorageKey);
            location.reload();
        },
        
        isLoggedIn: function() {
            return !!localStorage.getItem(CONFIG.storageKey);
        },
        
        showLogin: function() {
            localStorage.removeItem(CONFIG.storageKey);
            init();
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
