import React, { useState, useEffect, useRef } from 'react';
import styles from './InteractiveChatButton.module.css';

const InteractiveChatButton = ({ onChatOpen }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
const [suggestions] = useState([
    'What is Zero Moment Point?',
    'How do robot joints work?',
    'Explain inverse kinematics',
    'What are actuators?',
    'How do sensors work?'
  ]);
  const [currentSuggestion, setCurrentSuggestion] = useState(0);
  const inputRef = useRef(null);

  // Cycle through suggestions
  useEffect(() => {
    const interval = setInterval(() => {
      if (!isExpanded && !isHovered) {
        setCurrentSuggestion((prev) => (prev + 1) % suggestions.length);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [isExpanded, isHovered, suggestions.length]);

  // Focus input when expanded
  useEffect(() => {
    if (isExpanded && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isExpanded]);

  const handleExpand = () => {
    setIsExpanded(true);
    setIsHovered(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      setIsTyping(true);
      // Here you would integrate with the actual chatbot
      console.log('Sending message:', message);
      
      // Simulate typing response
      setTimeout(() => {
        setIsTyping(false);
        setMessage('');
        // Close after response
        setTimeout(() => {
          setIsExpanded(false);
        }, 1000);
      }, 2000);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setMessage(suggestion);
    setIsExpanded(true);
  };

  const handleClose = () => {
    setIsExpanded(false);
    setMessage('');
    setIsTyping(false);
  };

  return (
    <div 
      className={`${styles.chatButtonContainer} ${isExpanded ? styles.expanded : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Collapsed State */}
      {!isExpanded && (
        <button
          onClick={handleExpand}
          className={`${styles.chatButton} ${isHovered ? styles.hovered : ''}`}
          aria-label="Open chat assistant"
        >
          <div className={styles.buttonContent}>
            <div className={styles.chatIcon}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8.9h.5a8.48 8.48 0 0 1 8 8v.5z" 
                      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M9 10h.01M15 10h.01M9 14h.01M15 14h.01" 
                      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className={styles.buttonText}>Ask Robotics Tutor</span>
            <div className={styles.typingIndicator}>
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
          <div className={styles.suggestionBubble}>
            {suggestions[currentSuggestion]}
          </div>
        </button>
      )}

      {/* Expanded State */}
      {isExpanded && (
        <div className={styles.expandedChat}>
          <div className={styles.chatHeader}>
            <div className={styles.headerContent}>
              <div className={styles.chatIconExpanded}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8.9h.5a8.48 8.48 0 0 1 8 8v.5z" 
                        fill="currentColor"/>
                  <path d="M9 10h.01M15 10h.01M9 14h.01M15 14h.01" 
                        fill="white"/>
                </svg>
              </div>
              <div className={styles.headerText}>
                <h3>Robotics Tutor</h3>
                <p>Ask me anything about robotics!</p>
              </div>
            </div>
            <button 
              onClick={handleClose}
              className={styles.closeButton}
              aria-label="Close chat"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>

          {/* Suggestions */}
          <div className={styles.suggestionsList}>
            <p className={styles.suggestionsTitle}>Try asking:</p>
            <div className={styles.suggestionChips}>
              {suggestions.slice(0, 3).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className={styles.suggestionChip}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className={styles.chatForm}>
            <div className={styles.inputContainer}>
              <input
                ref={inputRef}
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask me about robotics..."
                className={styles.chatInput}
                disabled={isTyping}
              />
              <button
                type="submit"
                disabled={!message.trim() || isTyping}
                className={styles.sendButton}
                aria-label="Send message"
              >
                {isTyping ? (
                  <div className={styles.typingSpinner}>
                    <div></div>
                    <div></div>
                    <div></div>
                  </div>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9 5 4 9Z" 
                          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </button>
            </div>
          </form>

          {/* Typing Indicator */}
          {isTyping && (
            <div className={styles.typingMessage}>
              <div className={styles.typingAvatar}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8.9h.5a8.48 8.48 0 0 1 8 8v.5z" 
                        fill="currentColor"/>
                </svg>
              </div>
              <div className={styles.typingText}>
                <span>Robotics Tutor is typing</span>
                <div className={styles.typingDots}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InteractiveChatButton;