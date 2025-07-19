"""
BitBraniac Chatbot Service with LangChain integration and persistent chat history.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from flask import current_app
from .chat_history_service import ChatHistoryService


class BitBraniacChatbot:
    """BitBraniac AI Chatbot with persistent chat history."""
    
    def __init__(self, config):
        """Initialize the chatbot with configuration."""
        self.config = config
        self.llm = None
        self.memory = None
        self.window_memory = None
        self.chain = None
        self._setup_llm()
        self._setup_memory()
        self._setup_chain()
    
    def _setup_llm(self):
        """Set up the Google Generative AI model."""
        try:
            api_key = self.config.GOOGLE_API_KEY
            if not api_key:
                raise ValueError("Google API key not found in configuration")
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.MODEL_NAME,
                temperature=self.config.MODEL_TEMPERATURE,
                max_output_tokens=self.config.MAX_OUTPUT_TOKENS,
                google_api_key=api_key
            )
            
            current_app.logger.info(f"LLM initialized with model: {self.config.MODEL_NAME}")
            
        except Exception as e:
            current_app.logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def _setup_memory(self):
        """Set up conversation memory."""
        try:
            # Buffer memory for maintaining conversation context
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                input_key="input",
                output_key="output"
            )
            
            # Window memory for recent context (fallback)
            self.window_memory = ConversationBufferWindowMemory(
                k=self.config.CONVERSATION_WINDOW_SIZE,
                memory_key="recent_chat_history",
                return_messages=True,
                input_key="input",
                output_key="output"
            )
            
            current_app.logger.info("Memory systems initialized")
            
        except Exception as e:
            current_app.logger.error(f"Failed to initialize memory: {str(e)}")
            raise
    
    def _setup_chain(self):
        """Set up the LangChain conversation chain."""
        try:
            # System prompt for BitBraniac
            system_prompt = """You are BitBraniac 🧠, an AI-powered Computer Science tutor! Your mission is to help students learn and understand CS concepts through engaging, clear, and comprehensive explanations.

Your personality:
- Enthusiastic and encouraging about Computer Science
- Patient and supportive with students at all levels
- Use emojis occasionally to make conversations more engaging
- Break down complex topics into digestible parts
- Provide practical examples and real-world applications
- Ask follow-up questions to ensure understanding

Your expertise covers:
- Programming languages (Python, Java, C++, JavaScript, etc.)
- Data structures and algorithms
- Software engineering principles
- Database design and management
- Computer networks and security
- Machine learning and AI concepts
- Web development (frontend and backend)
- System design and architecture

Teaching approach:
- Start with fundamentals and build up complexity
- Use analogies and metaphors to explain difficult concepts
- Provide code examples when relevant
- Suggest practice problems or projects
- Encourage hands-on learning
- Be patient with mistakes and guide towards correct understanding

Remember: You're not just answering questions, you're nurturing the next generation of computer scientists! 🚀"""

            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # Create the chain
            self.chain = (
                RunnablePassthrough.assign(
                    chat_history=lambda x: self.memory.chat_memory.messages
                )
                | prompt
                | self.llm
                | StrOutputParser()
            )
            
            current_app.logger.info("Conversation chain initialized")
            
        except Exception as e:
            current_app.logger.error(f"Failed to initialize chain: {str(e)}")
            raise
    
    def load_session_history(self, session_id, user_id):
        """Load chat history from database into memory."""
        try:
            # Get messages from database
            messages = ChatHistoryService.get_session_messages_for_memory(
                session_id, user_id, limit=self.config.CONVERSATION_WINDOW_SIZE * 2
            )
            
            # Clear current memory
            self.memory.clear()
            self.window_memory.clear()
            
            # Load messages into memory
            for msg in messages:
                if msg["type"] == "human":
                    self.memory.chat_memory.add_user_message(msg["content"])
                    self.window_memory.chat_memory.add_user_message(msg["content"])
                elif msg["type"] == "ai":
                    self.memory.chat_memory.add_ai_message(msg["content"])
                    self.window_memory.chat_memory.add_ai_message(msg["content"])
            
            current_app.logger.info(f"Loaded {len(messages)} messages from session {session_id}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to load session history: {str(e)}")
            return False
    
    def chat(self, message, session_id=None, user_id=None):
        """
        Process a chat message and return response.
        
        Args:
            message (str): User's message
            session_id (str, optional): Chat session ID for persistent history
            user_id (str, optional): User ID for session validation
            
        Returns:
            dict: Response containing success status, message, and session info
        """
        try:
            # If session_id is provided, load history and save messages
            if session_id and user_id:
                # Load existing session history
                self.load_session_history(session_id, user_id)
                
                # Save user message to database
                ChatHistoryService.add_message_to_session(
                    session_id, user_id, 'user', message
                )
            
            # Generate response using the chain
            response = self.chain.invoke({"input": message})
            
            # Add to memory for current conversation
            self.memory.chat_memory.add_user_message(message)
            self.memory.chat_memory.add_ai_message(response)
            self.window_memory.chat_memory.add_user_message(message)
            self.window_memory.chat_memory.add_ai_message(response)
            
            # Save assistant response to database if session exists
            if session_id and user_id:
                ChatHistoryService.add_message_to_session(
                    session_id, user_id, 'assistant', response
                )
            
            return {
                'success': True,
                'response': response,
                'session_id': session_id
            }
            
        except Exception as e:
            current_app.logger.error(f"Chat processing error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to process message. Please try again.',
                'session_id': session_id
            }
    
    def get_welcome_message(self):
        """Get the welcome message for new users."""
        return """Hello, World! 👋 I'm **BitBraniac** 🧠, your AI-powered CS tutor!

Ask me anything about **programming, algorithms, databases, AI, and more!** Let's dive into the world of Computer Science! 🚀"""
    
    def clear_memory(self):
        """Clear conversation memory."""
        try:
            self.memory.clear()
            self.window_memory.clear()
            current_app.logger.info("Memory cleared")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to clear memory: {str(e)}")
            return False
    
    def get_conversation_history(self):
        """Get current conversation history."""
        try:
            messages = []
            for message in self.memory.chat_memory.messages:
                if isinstance(message, HumanMessage):
                    messages.append({"type": "human", "content": message.content})
                elif isinstance(message, AIMessage):
                    messages.append({"type": "ai", "content": message.content})
            
            return {
                'success': True,
                'history': messages
            }
            
        except Exception as e:
            current_app.logger.error(f"Failed to get conversation history: {str(e)}")
            return {
                'success': False,
                'history': []
            }

