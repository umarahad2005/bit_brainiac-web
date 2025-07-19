"""
Authentication service for BitBraniac application.
"""

from flask import current_app
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity
from datetime import timedelta
import re
from .models import User, db

# Initialize JWT manager
jwt = JWTManager()

def init_jwt(app):
    """Initialize JWT with the Flask app."""
    jwt.init_app(app)
    
    # Configure JWT settings
    app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """Define how to get user identity from user object."""
        return user.id
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user from JWT token."""
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()


class AuthService:
    """Service class for handling authentication operations."""
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength."""
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        # Add more password validation rules as needed
        # if not re.search(r'[A-Z]', password):
        #     return False, "Password must contain at least one uppercase letter"
        # if not re.search(r'[a-z]', password):
        #     return False, "Password must contain at least one lowercase letter"
        # if not re.search(r'\d', password):
        #     return False, "Password must contain at least one digit"
        
        return True, "Password is valid"
    
    @staticmethod
    def register_user(email, password):
        """Register a new user."""
        try:
            # Validate email format
            if not AuthService.validate_email(email):
                return {
                    'success': False,
                    'message': 'Invalid email format'
                }
            
            # Validate password
            is_valid, message = AuthService.validate_password(password)
            if not is_valid:
                return {
                    'success': False,
                    'message': message
                }
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email.lower()).first()
            if existing_user:
                return {
                    'success': False,
                    'message': 'User with this email already exists'
                }
            
            # Create new user
            user = User(email=email.lower())
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Generate tokens
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            return {
                'success': False,
                'message': 'Registration failed. Please try again.'
            }
    
    @staticmethod
    def login_user(email, password):
        """Authenticate user and return tokens."""
        try:
            # Find user by email
            user = User.query.filter_by(email=email.lower()).first()
            
            if not user or not user.check_password(password):
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            if not user.is_active:
                return {
                    'success': False,
                    'message': 'Account is deactivated'
                }
            
            # Generate tokens
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return {
                'success': False,
                'message': 'Login failed. Please try again.'
            }
    
    @staticmethod
    def refresh_token():
        """Refresh access token using refresh token."""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.filter_by(id=current_user_id).first()
            
            if not user or not user.is_active:
                return {
                    'success': False,
                    'message': 'User not found or inactive'
                }
            
            new_access_token = create_access_token(identity=user)
            
            return {
                'success': True,
                'access_token': new_access_token
            }
            
        except Exception as e:
            current_app.logger.error(f"Token refresh error: {str(e)}")
            return {
                'success': False,
                'message': 'Token refresh failed'
            }
    
    @staticmethod
    def get_current_user():
        """Get current authenticated user."""
        try:
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return None
            
            user = User.query.filter_by(id=current_user_id).first()
            return user if user and user.is_active else None
            
        except Exception as e:
            current_app.logger.error(f"Get current user error: {str(e)}")
            return None

