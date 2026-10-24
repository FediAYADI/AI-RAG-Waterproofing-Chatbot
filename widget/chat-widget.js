/**
 * AI RAG Waterproofing Chatbot - Embeddable Widget
 * 
 * Usage:
 * 1. Include this script on your website
 * 2. Initialize with: WaterproofingChatbot.init({ apiUrl: 'YOUR_API_URL' })
 */

(function(window) {
  'use strict';

  class WaterproofingChatbot {
    constructor(config) {
      this.config = {
        apiUrl: config.apiUrl || 'http://localhost:8000/api/v1',
        position: config.position || 'bottom-right',
        primaryColor: config.primaryColor || '#007bff',
        title: config.title || 'Waterproofing Assistant',
        placeholder: config.placeholder || 'Ask about waterproofing...',
        ...config
      };
      
      this.sessionId = this.generateSessionId();
      this.isOpen = false;
      this.messages = [];
      this.init();
    }

    generateSessionId() {
      return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    init() {
      this.injectStyles();
      this.createWidget();
      this.attachEventListeners();
    }

    injectStyles() {
      const style = document.createElement('style');
      style.textContent = `
        .wp-chat-widget-container {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 9999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .wp-chat-widget-container.bottom-left {
          right: auto;
          left: 20px;
        }

        .wp-chat-toggle-btn {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: ${this.config.primaryColor};
          border: none;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.3s ease;
        }

        .wp-chat-toggle-btn:hover {
          transform: scale(1.1);
        }

        .wp-chat-toggle-btn svg {
          width: 30px;
          height: 30px;
          fill: white;
        }

        .wp-chat-window {
          position: absolute;
          bottom: 80px;
          right: 0;
          width: 380px;
          height: 500px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
          display: none;
          flex-direction: column;
          overflow: hidden;
        }

        .wp-chat-window.open {
          display: flex;
        }

        .wp-chat-header {
          background: ${this.config.primaryColor};
          color: white;
          padding: 16px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .wp-chat-header h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
        }

        .wp-chat-close-btn {
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          font-size: 20px;
          padding: 0;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .wp-chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .wp-chat-welcome {
          text-align: center;
          color: #666;
          padding: 40px 20px;
        }

        .wp-chat-message {
          max-width: 80%;
          padding: 10px 14px;
          border-radius: 12px;
          line-height: 1.4;
        }

        .wp-chat-message.user {
          align-self: flex-end;
          background: ${this.config.primaryColor};
          color: white;
          border-bottom-right-radius: 4px;
        }

        .wp-chat-message.assistant {
          align-self: flex-start;
          background: #f0f0f0;
          color: #333;
          border-bottom-left-radius: 4px;
        }

        .wp-chat-input-area {
          padding: 12px;
          border-top: 1px solid #e0e0e0;
          display: flex;
          gap: 8px;
        }

        .wp-chat-input {
          flex: 1;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 8px;
          resize: none;
          font-family: inherit;
          font-size: 14px;
        }

        .wp-chat-input:focus {
          outline: none;
          border-color: ${this.config.primaryColor};
        }

        .wp-chat-send-btn {
          padding: 10px 20px;
          background: ${this.config.primaryColor};
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
        }

        .wp-chat-send-btn:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        .wp-chat-typing {
          text-align: center;
          color: #999;
          font-style: italic;
          padding: 8px;
        }

        @media (max-width: 480px) {
          .wp-chat-window {
            width: calc(100vw - 40px);
            height: 60vh;
          }
        }
      `;
      document.head.appendChild(style);
    }

    createWidget() {
      const container = document.createElement('div');
      container.className = `wp-chat-widget-container ${this.config.position}`;
      
      container.innerHTML = `
        <div class="wp-chat-window" id="wpChatWindow">
          <div class="wp-chat-header">
            <h3>${this.config.title}</h3>
            <button class="wp-chat-close-btn" id="wpChatClose">&times;</button>
          </div>
          <div class="wp-chat-messages" id="wpChatMessages">
            <div class="wp-chat-welcome">
              <p>👋 Welcome! Ask me anything about waterproofing solutions.</p>
            </div>
          </div>
          <div class="wp-chat-input-area">
            <textarea 
              class="wp-chat-input" 
              id="wpChatInput" 
              placeholder="${this.config.placeholder}"
              rows="2"
            ></textarea>
            <button class="wp-chat-send-btn" id="wpChatSend">Send</button>
          </div>
        </div>
        <button class="wp-chat-toggle-btn" id="wpChatToggle">
          <svg viewBox="0 0 24 24">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
          </svg>
        </button>
      `;
      
      document.body.appendChild(container);
    }

    attachEventListeners() {
      const toggleBtn = document.getElementById('wpChatToggle');
      const closeBtn = document.getElementById('wpChatClose');
      const sendBtn = document.getElementById('wpChatSend');
      const input = document.getElementById('wpChatInput');

      toggleBtn.addEventListener('click', () => this.toggle());
      closeBtn.addEventListener('click', () => this.toggle());
      sendBtn.addEventListener('click', () => this.sendMessage());
      
      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }

    toggle() {
      this.isOpen = !this.isOpen;
      const window = document.getElementById('wpChatWindow');
      window.classList.toggle('open', this.isOpen);
    }

    async sendMessage() {
      const input = document.getElementById('wpChatInput');
      const message = input.value.trim();
      
      if (!message) return;

      this.addMessage(message, 'user');
      input.value = '';
      
      this.showTyping();

      try {
        const response = await fetch(`${this.config.apiUrl}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: message,
            session_id: this.sessionId,
            use_rag: true
          })
        });

        const data = await response.json();
        this.hideTyping();
        this.addMessage(data.answer, 'assistant');
      } catch (error) {
        this.hideTyping();
        this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        console.error('Error:', error);
      }
    }

    addMessage(content, role) {
      const messagesContainer = document.getElementById('wpChatMessages');
      const welcomeMessage = messagesContainer.querySelector('.wp-chat-welcome');
      
      if (welcomeMessage) {
        welcomeMessage.remove();
      }

      const messageDiv = document.createElement('div');
      messageDiv.className = `wp-chat-message ${role}`;
      messageDiv.textContent = content;
      messagesContainer.appendChild(messageDiv);
      
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTyping() {
      const messagesContainer = document.getElementById('wpChatMessages');
      const typingDiv = document.createElement('div');
      typingDiv.className = 'wp-chat-typing';
      typingDiv.id = 'wpChatTyping';
      typingDiv.textContent = 'AI is thinking...';
      messagesContainer.appendChild(typingDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
      const typingDiv = document.getElementById('wpChatTyping');
      if (typingDiv) {
        typingDiv.remove();
      }
    }
  }

  // Expose to global scope
  window.WaterproofingChatbot = {
    init: function(config) {
      return new WaterproofingChatbot(config);
    }
  };

})(window);
