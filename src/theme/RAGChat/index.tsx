import React, { useState, useEffect, useRef, useCallback } from 'react';
import styles from './styles.module.css';
import { createTextSelectionManager } from './textSelection';
import { createViewportDetector } from './viewport';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  sources?: string[];
  contextChunks?: string[];
}

interface WebSocketMessage {
  type: 'welcome' | 'response_start' | 'response_chunk' | 'response_end' | 'error' | 'pong';
  data?: any;
  timestamp?: number;
}

interface RAGChatProps {
  websocketUrl?: string;
  maxMessages?: number;
  showSources?: boolean;
  enableTextSelection?: boolean;
}

const RAGChat: React.FC<RAGChatProps> = ({
  websocketUrl = process.env.NODE_ENV === 'production' 
    ? 'wss://your-backend-domain.com/ws/chat' 
    : 'ws://localhost:8000/ws/chat',
  maxMessages = 50,
  showSources = true,
  enableTextSelection = true,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [contextChunks, setContextChunks] = useState<string[]>([]);
  const [isMinimized, setIsMinimized] = useState(false);
  const [currentQueryId, setCurrentQueryId] = useState<string | null>(null);
  
  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Viewport detection
  const [viewportInfo, setViewportInfo] = useState(() => {
    const detector = createViewportDetector();
    return detector ? detector.getCurrentInfo() : {
      width: 1024,
      height: 768,
      isMobile: false,
      isTablet: false,
      isDesktop: true,
      orientation: 'landscape',
      devicePixelRatio: 1,
      touchSupport: false,
    };
  });

  // Update viewport info on changes
  useEffect(() => {
    const viewportDetector = createViewportDetector();
    
    if (!viewportDetector) {
      return;
    }

    const handleViewportChange = (info: any) => {
      setViewportInfo(info);
    };

    viewportDetector.addListener(handleViewportChange);

    return () => {
      viewportDetector.removeListener(handleViewportChange);
    };
  }, []);

  // Auto-scroll to latest message
  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, []);

  // Handle text selection
  useEffect(() => {
    if (enableTextSelection) {
      const textSelectionManager = createTextSelectionManager();
      
      if (!textSelectionManager) {
        return;
      }

      const handleTextSelection = (event: any) => {
        if (event.type === 'text_selected') {
          const selectedText = event.data.text;
          if (selectedText && selectedText.trim()) {
            setContextChunks(prev => {
              const newChunks = [selectedText, ...prev.slice(0, 4)]; // Keep max 5 chunks
              return newChunks;
            });
          }
        }
      };

      textSelectionManager.addListener(handleTextSelection);
      
      return () => {
        textSelectionManager.destroy();
      };
    }
  }, [enableTextSelection]);

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        ws.current = new WebSocket(websocketUrl);
        
        ws.current.onopen = () => {
          setIsConnected(true);
          console.log('WebSocket connected');
        };
        
        ws.current.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            handleWebSocketMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        ws.current.onclose = () => {
          setIsConnected(false);
          console.log('WebSocket disconnected');
          
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };
        
        ws.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
        };
        
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
      }
    };

    connectWebSocket();
    
    return () => {
      if (ws.current) {
        ws.current.close();
        ws.current = null;
      }
    };
  }, [websocketUrl]);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'welcome':
        console.log('Connected to RAG chat server');
        break;
        
      case 'response_start':
        setIsStreaming(true);
        setCurrentQueryId(message.data?.query_id || null);
        
        // Add assistant message placeholder
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          type: 'assistant',
          content: '',
          timestamp: new Date(),
          sources: message.data?.sources || [],
          contextChunks: contextChunks
        };
        
        setMessages(prev => [...prev.slice(-maxMessages + 1), assistantMessage]);
        break;
        
      case 'response_chunk':
        if (message.data?.query_id === currentQueryId) {
          setMessages(prev => {
            const updated = [...prev];
            const lastMessage = updated[updated.length - 1];
            
            if (lastMessage && lastMessage.type === 'assistant') {
              lastMessage.content += message.data.content || '';
            }
            
            return updated;
          });
        }
        break;
        
      case 'response_end':
        setIsStreaming(false);
        setCurrentQueryId(null);
        
        // Update final message metadata
        setMessages(prev => {
          const updated = [...prev];
          const lastMessage = updated[updated.length - 1];
          
          if (lastMessage && lastMessage.type === 'assistant') {
            lastMessage.timestamp = new Date();
          }
          
          return updated;
        });
        break;
        
      case 'error':
        setIsStreaming(false);
        setCurrentQueryId(null);
        
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          type: 'system',
          content: `Error: ${message.data?.error || 'Unknown error occurred'}`,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev.slice(-maxMessages + 1), errorMessage]);
        break;
        
      case 'pong':
        // Handle ping/pong for connection health
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  }, [currentQueryId, contextChunks, maxMessages]);

  // Send message to WebSocket
  const sendMessage = useCallback(() => {
    if (!input.trim() || !ws.current || ws.current.readyState !== WebSocket.OPEN) {
      return;
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
      contextChunks: contextChunks
    };

    // Add user message immediately
    setMessages(prev => [...prev.slice(-maxMessages + 1), userMessage]);
    
    // Send to WebSocket
    const message = {
      type: 'question',
      data: {
        question: input.trim(),
        context_chunks: contextChunks
      }
    };

    ws.current.send(JSON.stringify(message));
    setInput('');
    setContextChunks([]);
  }, [input, contextChunks, ws]);

  // Handle input key press
  const handleKeyPress = useCallback((event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }, [sendMessage]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 80)}px`;
    }
  }, [input]);

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Clear context
  const clearContext = useCallback(() => {
    setContextChunks([]);
    const textSelectionManager = createTextSelectionManager();
    if (textSelectionManager) {
      textSelectionManager.removeHighlights();
    }
  }, []);

  // Toggle minimize
  const toggleMinimize = useCallback(() => {
    setIsMinimized(prev => !prev);
  }, []);

  // Get responsive dimensions based on viewport
  const chatDimensions = viewportInfo.isMobile 
    ? { width: '90%', height: '400px' }
    : viewportInfo.isTablet
    ? { width: '450px', height: '500px' }
    : { width: '350px', height: '500px' };

  return (
    <div 
      className={`${styles.ragChatWidget} ${isMinimized ? styles.ragChatWidgetMinimized : ''} ${!isConnected ? styles.ragChatWidgetDisconnected : ''} ${viewportInfo.isMobile ? styles.ragChatWidgetMobile : ''}`}
      style={viewportInfo.isMobile ? chatDimensions : undefined}
    >
      {/* Header */}
      <div className={styles.ragChatHeader}>
        <h4>Robotics Tutor</h4>
        <div className={styles.ragChatControls}>
          <div 
            className={`${styles.ragChatStatus} ${isConnected ? styles.ragChatStatusConnected : styles.ragChatStatusDisconnected}`}
            title={isConnected ? 'Connected' : 'Disconnected'}
          />
          <button
            className={styles.ragChatMinimize}
            onClick={toggleMinimize}
            title={isMinimized ? 'Expand' : 'Minimize'}
          >
            {isMinimized ? '▲' : '▼'}
          </button>
        </div>
      </div>

      {/* Context Display */}
      {contextChunks.length > 0 && !isMinimized && (
        <div className={styles.ragChatContextDisplay}>
          <div className={styles.ragChatContextTitle}>
            <span>Context ({contextChunks.length} chunks)</span>
            <button
              className={styles.ragChatContextClear}
              onClick={clearContext}
              title="Clear context"
            >
              ✕
            </button>
          </div>
          <div className={styles.ragChatContextChunks}>
            {contextChunks.map((chunk, index) => (
              <div key={index} className={styles.ragChatContextChunk}>
                {chunk.length > 100 ? `${chunk.substring(0, 100)}...` : chunk}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      {!isMinimized && (
        <div className={styles.ragChatMessages} ref={messagesEndRef}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`${styles.message} ${styles[message.type]}`}
            >
              <div className={styles.messageContent}>
                {message.content}
                {message.type === 'assistant' && showSources && message.sources && message.sources.length > 0 && (
                  <div className={styles.messageSources}>
                    <strong>Sources:</strong> {message.sources.join(', ')}
                  </div>
                )}
              </div>
              <div className={styles.messageTime}>
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Input */}
      {!isMinimized && (
        <div className={styles.ragChatInputContainer}>
          <textarea
            ref={inputRef}
            className={styles.ragChatInputField}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about robotics..."
            disabled={!isConnected || isStreaming}
            rows={1}
          />
          <button
            className={styles.ragChatSendButton}
            onClick={sendMessage}
            disabled={!isConnected || isStreaming || !input.trim()}
          >
            {isStreaming ? (
              <div className={styles.ragChatTypingIndicator}>
                <div className={styles.ragChatTypingDots}>
                  <div className={styles.ragChatTypingDot}></div>
                  <div className={styles.ragChatTypingDot}></div>
                  <div className={styles.ragChatTypingDot}></div>
                </div>
              </div>
            ) : (
              'Send'
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default RAGChat;