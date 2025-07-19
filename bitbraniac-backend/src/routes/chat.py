"""
Chat routes for BitBraniac application with authentication and session support.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.chatbot_service import BitBraniacChatbot
from ..services.chat_history_service import ChatHistoryService

chat_bp = Blueprint('chat', __name__)

# Global chatbot instance
chatbot = None

def get_chatbot():
    """Get or create chatbot instance."""
    global chatbot
    if chatbot is None:
        chatbot = BitBraniacChatbot(current_app.config)
    return chatbot


@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for chat service."""
    return jsonify({
        'status': 'healthy',
        'service': 'BitBraniac Chat API',
        'version': '2.0.0',
        'features': ['authentication', 'persistent_history', 'ai_tutoring'],
        'success': True
    })


@chat_bp.route('/welcome', methods=['GET'])
def get_welcome_message():
    """Get the welcome message."""
    try:
        bot = get_chatbot()
        welcome_message = bot.get_welcome_message()
        
        return jsonify({
            'message': welcome_message,
            'success': True
        })
        
    except Exception as e:
        current_app.logger.error(f"Welcome message error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get welcome message'
        }), 500


@chat_bp.route('/message', methods=['POST'])
@jwt_required()
def send_message():
    """Send a message to BitBraniac with session support."""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'Message is required'
            }), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message cannot be empty'
            }), 400
        
        session_id = data.get('session_id')
        
        # If no session_id provided, create a new session
        if not session_id:
            session_result = ChatHistoryService.create_chat_session(user_id)
            if session_result['success']:
                session_id = session_result['session']['id']
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to create chat session'
                }), 500
        
        # Get chatbot and process message
        bot = get_chatbot()
        result = bot.chat(message, session_id=session_id, user_id=user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'response': result['response'],
                'session_id': session_id
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Failed to process message')
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Send message error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to process message'
        }), 500


@chat_bp.route('/message/anonymous', methods=['POST'])
def send_message_anonymous():
    """Send a message to BitBraniac without authentication (temporary session)."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'Message is required'
            }), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message cannot be empty'
            }), 400
        
        # Get chatbot and process message without session persistence
        bot = get_chatbot()
        result = bot.chat(message)
        
        if result['success']:
            return jsonify({
                'success': True,
                'response': result['response']
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Failed to process message')
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Send anonymous message error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to process message'
        }), 500


@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    """Get current conversation history from memory."""
    try:
        bot = get_chatbot()
        result = bot.get_conversation_history()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Get chat history error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get chat history'
        }), 500


@chat_bp.route('/clear', methods=['POST'])
@jwt_required()
def clear_chat():
    """Clear current conversation memory."""
    try:
        bot = get_chatbot()
        success = bot.clear_memory()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Chat memory cleared successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to clear chat memory'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Clear chat error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to clear chat'
        }), 500

