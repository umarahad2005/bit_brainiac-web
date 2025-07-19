"""
Chat session management routes for BitBraniac application.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.chat_history_service import ChatHistoryService
from ..auth import AuthService

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """Get all chat sessions for the current user."""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        limit = request.args.get('limit', 50, type=int)
        result = ChatHistoryService.get_user_chat_sessions(user_id, limit)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve chat sessions'
        }), 500


@sessions_bp.route('/', methods=['POST'])
@jwt_required()
def create_session():
    """Create a new chat session."""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        data = request.get_json() or {}
        title = data.get('title', 'New Chat')
        
        result = ChatHistoryService.create_chat_session(user_id, title)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to create chat session'
        }), 500


@sessions_bp.route('/<session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """Get a specific chat session with messages."""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        result = ChatHistoryService.get_chat_session(session_id, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'not found' in result['message'] else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve chat session'
        }), 500


@sessions_bp.route('/<session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """Delete a chat session."""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        result = ChatHistoryService.delete_chat_session(session_id, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'not found' in result['message'] else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to delete chat session'
        }), 500


@sessions_bp.route('/clear', methods=['POST'])
@jwt_required()
def clear_all_sessions():
    """Clear all chat sessions for the current user."""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        result = ChatHistoryService.clear_all_user_sessions(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to clear chat sessions'
        }), 500

