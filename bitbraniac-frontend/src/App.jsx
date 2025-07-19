import React, { useState, useEffect, useRef } from 'react';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { ChatSidebar } from './components/chat/ChatSidebar';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { ChatProvider, useChat } from './contexts/ChatContext';
import { useAuth } from './contexts/AuthContext';
import { Button } from './components/ui/button';
import { Separator } from './components/ui/separator';
import { Alert, AlertDescription } from './components/ui/alert';
import { Loader2, MessageSquare, Trash2, Menu, X } from 'lucide-react';
import { chatService } from './services/chatService';
import './App.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);
  
  const { currentSession, updateSessionInList, setError: setChatError } = useChat();
  const { isAuthenticated } = useAuth();

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load session messages when current session changes
  useEffect(() => {
    if (currentSession && currentSession.messages) {
      const formattedMessages = currentSession.messages.map(msg => ({
        type: msg.message_type,
        content: msg.content,
        timestamp: msg.created_at
      }));
      setMessages(formattedMessages);
    } else if (!currentSession) {
      setMessages([]);
    }
  }, [currentSession]);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
    loadWelcomeMessage();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkBackendHealth = async () => {
    try {
      const result = await chatService.checkHealth();
      setConnectionStatus(result.success ? 'connected' : 'disconnected');
    } catch (error) {
      setConnectionStatus('disconnected');
    }
  };

  const loadWelcomeMessage = async () => {
    if (messages.length === 0) {
      try {
        const result = await chatService.getWelcomeMessage();
        if (result.success) {
          setMessages([{
            type: 'assistant',
            content: result.message,
            timestamp: new Date().toISOString()
          }]);
        }
      } catch (error) {
        console.error('Failed to load welcome message:', error);
      }
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    setError(null);
    setIsLoading(true);

    // Add user message to UI immediately
    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const result = await chatService.sendMessage(message, currentSession?.id);
      
      if (result.success) {
        // Add assistant response
        const assistantMessage = {
          type: 'assistant',
          content: result.response,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, assistantMessage]);

        // Update session info if available
        if (result.session_id && currentSession) {
          const updatedSession = {
            ...currentSession,
            updated_at: new Date().toISOString(),
            message_count: (currentSession.message_count || 0) + 2
          };
          updateSessionInList(updatedSession);
        }
      } else {
        setError(result.message || 'Failed to send message');
        // Remove the user message if sending failed
        setMessages(prev => prev.slice(0, -1));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to send message. Please try again.');
      // Remove the user message if sending failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear this chat?')) {
      setMessages([]);
      loadWelcomeMessage();
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      {isAuthenticated && (
        <div className={`
          fixed lg:relative lg:translate-x-0 transition-transform duration-300 ease-in-out z-50
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          w-80 h-full
        `}>
          <ChatSidebar />
        </div>
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex items-center space-x-3">
            {isAuthenticated && (
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
              </Button>
            )}
            
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                🧠
              </div>
              <div>
                <h1 className="font-semibold">
                  {currentSession?.title || 'BitBraniac'}
                </h1>
                <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                  <div className={`w-2 h-2 rounded-full ${
                    connectionStatus === 'connected' ? 'bg-green-500' : 
                    connectionStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
                  }`} />
                  <span>
                    {connectionStatus === 'connected' ? 'Connected' : 
                     connectionStatus === 'disconnected' ? 'Disconnected' : 'Connecting...'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearChat}
              disabled={messages.length === 0}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-4">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">Welcome to BitBraniac!</p>
                <p className="text-sm">Start a conversation to begin learning.</p>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage
                key={index}
                type={message.type}
                content={message.content}
                timestamp={message.timestamp}
              />
            ))
          )}
          
          {isLoading && (
            <div className="flex items-center space-x-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>BitBraniac is thinking...</span>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <Separator />

        {/* Input */}
        <div className="p-4">
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isLoading || connectionStatus === 'disconnected'}
            placeholder={
              connectionStatus === 'disconnected' 
                ? 'Disconnected from server...' 
                : 'Ask me anything about Computer Science...'
            }
          />
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <ProtectedRoute>
          <ChatInterface />
        </ProtectedRoute>
      </ChatProvider>
    </AuthProvider>
  );
}

export default App;

