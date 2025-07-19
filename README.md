# BitBraniac - Enhanced AI CS Tutor

**Version 2.0** - Now with User Authentication & Persistent Chat History!

BitBraniac is an AI-powered Computer Science tutor built with Flask (backend) and React (frontend), featuring user authentication, persistent chat history, and session management - similar to ChatGPT's interface.

## 🆕 New Features in Version 2.0

### 🔐 User Authentication
- **Email/Password Registration & Login**
- **JWT Token-based Authentication**
- **Secure Session Management**
- **Protected Routes**

### 💾 Persistent Chat History
- **SQLite Database Storage**
- **Multiple Chat Sessions per User**
- **Session Titles Auto-generated from First Message**
- **Create New Chat / Continue Existing Chat**
- **Delete Individual Sessions**

### 🎨 Enhanced User Interface
- **ChatGPT-like Sidebar with Session List**
- **Mobile-Responsive Design**
- **Real-time Connection Status**
- **User Profile Management**
- **Modern UI with Tailwind CSS & shadcn/ui**

## 🏗️ Architecture

```
BitBraniac/
├── bitbraniac-backend/          # Flask API Server
│   ├── src/
│   │   ├── main.py             # Flask application entry point
│   │   ├── config.py           # Configuration management
│   │   ├── models.py           # SQLAlchemy database models
│   │   ├── auth.py             # JWT authentication service
│   │   ├── routes/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── chat.py         # Chat messaging endpoints
│   │   │   └── sessions.py     # Session management endpoints
│   │   └── services/
│   │       ├── chatbot_service.py      # LangChain integration
│   │       └── chat_history_service.py # Chat persistence
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Virtual environment
│
├── bitbraniac-frontend/         # React Application
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── contexts/
│   │   │   ├── AuthContext.jsx # Authentication state management
│   │   │   └── ChatContext.jsx # Chat session state management
│   │   ├── components/
│   │   │   ├── auth/           # Login/Register components
│   │   │   ├── chat/           # Chat interface components
│   │   │   └── ui/             # Reusable UI components
│   │   └── services/
│   │       ├── authService.js  # Authentication API calls
│   │       ├── chatService.js  # Chat API calls
│   │       └── sessionService.js # Session management API calls
│   └── package.json            # Node.js dependencies
│
└── Documentation/
    ├── README.md               # This file
    ├── DEPLOYMENT.md           # Deployment instructions
    └── API_DOCUMENTATION.md    # API endpoint documentation
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- **Google Gemini API Key** (for AI functionality)

### 1. Clone & Setup Backend

```bash
cd bitbraniac-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your-google-gemini-api-key"
export JWT_SECRET_KEY="your-secret-key-for-jwt"
export DATABASE_URL="sqlite:///bitbraniac.db"

# Run Flask server
python src/main.py
```

Backend will run on: `http://localhost:5002`

### 2. Setup Frontend

```bash
cd bitbraniac-frontend

# Install dependencies
pnpm install  # or npm install

# Set environment variables
export VITE_API_BASE_URL="http://localhost:5002/api"

# Run React development server
pnpm run dev  # or npm run dev
```

Frontend will run on: `http://localhost:5173`

### 3. Access Application

1. Open `http://localhost:5173` in your browser
2. **Register** a new account or **Login** with existing credentials
3. Start chatting with BitBraniac!

## 🔧 Configuration

### Environment Variables

#### Backend (.env or export)
```bash
GOOGLE_API_KEY=your_google_gemini_api_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=sqlite:///bitbraniac.db
FLASK_ENV=development
PORT=5002
```

#### Frontend (.env.local)
```bash
VITE_API_BASE_URL=http://localhost:5002/api
```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chat Sessions Table
```sql
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES chat_sessions(id),
    message_type VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user info

### Chat Sessions
- `GET /api/sessions` - List user's chat sessions
- `POST /api/sessions` - Create new chat session
- `GET /api/sessions/{id}` - Get specific session with messages
- `DELETE /api/sessions/{id}` - Delete chat session

### Chat Messages
- `POST /api/chat/message` - Send message (authenticated)
- `POST /api/chat/message/anonymous` - Send message (anonymous)
- `GET /api/chat/welcome` - Get welcome message
- `GET /api/health` - Health check

## 🎯 Features Comparison

| Feature | Version 1.0 | Version 2.0 |
|---------|-------------|-------------|
| AI Chat | ✅ | ✅ |
| LangChain Integration | ✅ | ✅ |
| Google Gemini Model | ✅ | ✅ |
| User Interface | Basic Gradio | Modern React |
| User Authentication | ❌ | ✅ Email/Password |
| Chat History | Session-based | ✅ Persistent Database |
| Multiple Sessions | ❌ | ✅ Unlimited Sessions |
| Mobile Support | Limited | ✅ Fully Responsive |
| Session Management | ❌ | ✅ Create/Delete/Switch |
| User Profiles | ❌ | ✅ Profile Management |

## 🛠️ Development

### Backend Development
```bash
cd bitbraniac-backend
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
export FLASK_ENV=development
python src/main.py
```

### Frontend Development
```bash
cd bitbraniac-frontend

# Install dependencies
pnpm install

# Run development server with hot reload
pnpm run dev

# Build for production
pnpm run build
```

### Database Management
```bash
# The database is automatically created on first run
# To reset the database, simply delete the SQLite file:
rm bitbraniac-backend/bitbraniac.db

# Restart the backend to recreate tables
python src/main.py
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Production deployment with Docker
- Environment configuration
- Database setup
- SSL/HTTPS configuration
- Performance optimization

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Configured for frontend domain
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **XSS Protection**: React's built-in protection

## 🧪 Testing

### Backend Testing
```bash
cd bitbraniac-backend
source venv/bin/activate

# Test API endpoints
curl -X POST http://localhost:5002/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Frontend Testing
```bash
cd bitbraniac-frontend

# Run tests (if configured)
pnpm test

# Build and preview
pnpm run build
pnpm run preview
```

## 📝 Changelog

### Version 2.0.0 (Current)
- ✅ Added user authentication with email/password
- ✅ Implemented persistent chat history with SQLite
- ✅ Created modern React frontend with Tailwind CSS
- ✅ Added session management (create/delete/switch)
- ✅ Implemented JWT-based security
- ✅ Added mobile-responsive design
- ✅ Created comprehensive API documentation

### Version 1.0.0
- ✅ Basic AI chat functionality
- ✅ LangChain integration
- ✅ Google Gemini model
- ✅ Gradio web interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the [API Documentation](API_DOCUMENTATION.md)
2. Review the [Deployment Guide](DEPLOYMENT.md)
3. Create an issue in the repository

## 🙏 Acknowledgments

- **LangChain** for AI framework
- **Google Gemini** for AI model
- **React** for frontend framework
- **Flask** for backend framework
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components

