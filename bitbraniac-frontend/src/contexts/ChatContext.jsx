import React, { createContext, useContext, useState, useEffect } from 'react';
import { sessionService } from '../services/sessionService';
import { useAuth } from './AuthContext';

const ChatContext = createContext();

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export const ChatProvider = ({ children }) => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { isAuthenticated } = useAuth();

  // Load user sessions when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadUserSessions();
    } else {
      setSessions([]);
      setCurrentSession(null);
    }
  }, [isAuthenticated]);

  const loadUserSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await sessionService.getUserSessions();
      
      if (result.success) {
        setSessions(result.sessions || []);
      } else {
        setError(result.message || 'Failed to load chat sessions');
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
      setError('Failed to load chat sessions');
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async (title = 'New Chat') => {
    try {
      setError(null);
      const result = await sessionService.createSession(title);
      
      if (result.success) {
        const newSession = result.session;
        setSessions(prev => [newSession, ...prev]);
        setCurrentSession(newSession);
        return newSession;
      } else {
        setError(result.message || 'Failed to create new chat session');
        return null;
      }
    } catch (error) {
      console.error('Failed to create session:', error);
      setError('Failed to create new chat session');
      return null;
    }
  };

  const loadSession = async (sessionId) => {
    try {
      setError(null);
      const result = await sessionService.getSession(sessionId);
      
      if (result.success) {
        setCurrentSession(result.session);
        return result.session;
      } else {
        setError(result.message || 'Failed to load chat session');
        return null;
      }
    } catch (error) {
      console.error('Failed to load session:', error);
      setError('Failed to load chat session');
      return null;
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      setError(null);
      const result = await sessionService.deleteSession(sessionId);
      
      if (result.success) {
        setSessions(prev => prev.filter(session => session.id !== sessionId));
        
        // If the deleted session was the current one, clear it
        if (currentSession && currentSession.id === sessionId) {
          setCurrentSession(null);
        }
        
        return true;
      } else {
        setError(result.message || 'Failed to delete chat session');
        return false;
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      setError('Failed to delete chat session');
      return false;
    }
  };

  const clearAllSessions = async () => {
    try {
      setError(null);
      const result = await sessionService.clearAllSessions();
      
      if (result.success) {
        setSessions([]);
        setCurrentSession(null);
        return true;
      } else {
        setError(result.message || 'Failed to clear chat sessions');
        return false;
      }
    } catch (error) {
      console.error('Failed to clear sessions:', error);
      setError('Failed to clear chat sessions');
      return false;
    }
  };

  const updateSessionInList = (updatedSession) => {
    setSessions(prev => 
      prev.map(session => 
        session.id === updatedSession.id ? updatedSession : session
      )
    );
    
    if (currentSession && currentSession.id === updatedSession.id) {
      setCurrentSession(updatedSession);
    }
  };

  const value = {
    sessions,
    currentSession,
    loading,
    error,
    loadUserSessions,
    createNewSession,
    loadSession,
    deleteSession,
    clearAllSessions,
    updateSessionInList,
    setCurrentSession,
    setError
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

