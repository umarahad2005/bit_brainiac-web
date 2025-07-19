"""
Chat history service for BitBraniac application.
"""

from flask import current_app
from datetime import datetime
from ..models import ChatSession, ChatMessage, db
from ..auth import AuthService


class ChatHistoryService:
    """Service class for handling chat history operations."""
    
    @staticmethod
    def create_chat_session(user_id, title=None):
        """Create a new chat session for a user."""
        try:
            session = ChatSession(
                user_id=user_id,
                title=title or "New Chat"
            )
            
            db.session.add(session)
            db.session.commit()
            
            return {
                'success': True,
                'session': session.to_dict(),
                'message': 'Chat session created successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Create chat session error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to create chat session'
            }
    
    @staticmethod
    def get_user_chat_sessions(user_id, limit=50):
        """Get all chat sessions for a user."""
        try:
            sessions = ChatSession.query.filter_by(
                user_id=user_id,
                is_active=True
            ).order_by(ChatSession.updated_at.desc()).limit(limit).all()
            
            return {
                'success': True,
                'sessions': [session.to_dict() for session in sessions]
            }
            
        except Exception as e:
            current_app.logger.error(f"Get user chat sessions error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to retrieve chat sessions'
            }
    
    @staticmethod
    def get_chat_session(session_id, user_id):
        """Get a specific chat session with messages."""
        try:
            session = ChatSession.query.filter_by(
                id=session_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            if not session:
                return {
                    'success': False,
                    'message': 'Chat session not found'
                }
            
            return {
                'success': True,
                'session': session.to_dict(include_messages=True)
            }
            
        except Exception as e:
            current_app.logger.error(f"Get chat session error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to retrieve chat session'
            }
    
    @staticmethod
    def add_message_to_session(session_id, user_id, message_type, content):
        """Add a message to a chat session."""
        try:
            # Verify session belongs to user
            session = ChatSession.query.filter_by(
                id=session_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            if not session:
                return {
                    'success': False,
                    'message': 'Chat session not found'
                }
            
            # Create new message
            message = ChatMessage(
                session_id=session_id,
                message_type=message_type,
                content=content
            )
            
            db.session.add(message)
            
            # Update session timestamp
            session.updated_at = datetime.utcnow()
            
            # Generate title from first user message if not set
            if not session.title or session.title == "New Chat":
                if message_type == 'user':
                    session.generate_title()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': message.to_dict(),
                'session': session.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Add message to session error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to add message to session'
            }
    
    @staticmethod
    def delete_chat_session(session_id, user_id):
        """Delete a chat session (soft delete)."""
        try:
            session = ChatSession.query.filter_by(
                id=session_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            if not session:
                return {
                    'success': False,
                    'message': 'Chat session not found'
                }
            
            # Soft delete
            session.is_active = False
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Chat session deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Delete chat session error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to delete chat session'
            }
    
    @staticmethod
    def clear_all_user_sessions(user_id):
        """Clear all chat sessions for a user (soft delete)."""
        try:
            sessions = ChatSession.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            for session in sessions:
                session.is_active = False
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Cleared {len(sessions)} chat sessions'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Clear all user sessions error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to clear chat sessions'
            }
    
    @staticmethod
    def get_session_messages_for_memory(session_id, user_id, limit=None):
        """Get messages from a session formatted for LangChain memory."""
        try:
            session = ChatSession.query.filter_by(
                id=session_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            if not session:
                return []
            
            query = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at.asc())
            
            if limit:
                # Get the most recent messages
                query = query.limit(limit)
            
            messages = query.all()
            
            # Format for LangChain memory
            formatted_messages = []
            for msg in messages:
                if msg.message_type == 'user':
                    formatted_messages.append({"type": "human", "content": msg.content})
                elif msg.message_type == 'assistant':
                    formatted_messages.append({"type": "ai", "content": msg.content})
            
            return formatted_messages
            
        except Exception as e:
            current_app.logger.error(f"Get session messages for memory error: {str(e)}")
            return []

