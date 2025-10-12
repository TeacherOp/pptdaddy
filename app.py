#!/usr/bin/env python3
"""
PPT Daddy Web Application
Flask-based web interface for AI-powered presentation generation
"""

import os
import json
import uuid
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from agent.main_chat import MainChat

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Store active chat sessions (in production, use Redis or database)
chat_sessions = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_or_create_session():
    """Get or create a chat session"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    session_id = session['session_id']

    if session_id not in chat_sessions:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        chat_sessions[session_id] = {
            'chat': MainChat(api_key=api_key),
            'messages': [],
            'pptx_file': None,
            'session_start_time': time.time()  # Track when session started
        }

    return session_id, chat_sessions[session_id]


@app.route('/')
def index():
    """Render the main page"""
    # Clear any existing session
    session.clear()
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        # Get or create session
        session_id, chat_session = get_or_create_session()

        message = request.form.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Handle file uploads
        uploaded_files = []
        if 'files[]' in request.files:
            files = request.files.getlist('files[]')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Create unique filename
                    unique_filename = f"{session_id}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    uploaded_files.append(filepath)

        # Determine if this is the first message
        is_first_message = len(chat_session['messages']) == 0

        # Store user message
        chat_session['messages'].append({
            'role': 'user',
            'content': message,
            'images': uploaded_files
        })

        # Get AI response
        if is_first_message:
            # Start conversation
            response = chat_session['chat'].start_conversation(
                message,
                uploaded_files if uploaded_files else None
            )
        else:
            # Continue conversation
            response = chat_session['chat'].send_message(
                message,
                uploaded_files if uploaded_files else None
            )

        # Store AI response
        chat_session['messages'].append({
            'role': 'assistant',
            'content': response
        })

        # Check if PPTX was generated - only look for files created AFTER this session started
        pptx_file = None
        session_start_time = chat_session.get('session_start_time', 0)

        # Check if there's a recent PPTX file in exports that was created after session started
        exports_dir = Path('exports')
        if exports_dir.exists():
            pptx_files = sorted(exports_dir.glob('*.pptx'), key=os.path.getmtime, reverse=True)
            # Only consider files created after the session started
            for pptx_path in pptx_files:
                if os.path.getmtime(pptx_path) > session_start_time:
                    pptx_file = str(pptx_path)
                    chat_session['pptx_file'] = pptx_file
                    break

        return jsonify({
            'success': True,
            'response': response,
            'has_pptx': pptx_file is not None,
            'pptx_filename': os.path.basename(pptx_file) if pptx_file else None
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/download')
def download():
    """Download the generated PPTX file"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in chat_sessions:
            return jsonify({'error': 'No active session'}), 404

        chat_session = chat_sessions[session_id]
        pptx_file = chat_session.get('pptx_file')

        if not pptx_file or not os.path.exists(pptx_file):
            return jsonify({'error': 'No presentation file found'}), 404

        return send_file(
            pptx_file,
            as_attachment=True,
            download_name=os.path.basename(pptx_file)
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset the current session"""
    try:
        session_id = session.get('session_id')
        if session_id and session_id in chat_sessions:
            del chat_sessions[session_id]
        session.clear()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    """Run the Flask application"""

    # Ensure required directories exist
    Path("slides").mkdir(exist_ok=True)
    Path("exports").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("   Please set it in your .env file")
        return

    # Get configuration
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"

    print("\n" + "="*60)
    print("🎨 PPT DADDY - Web Interface")
    print("="*60)
    print(f"\n🌐 Open your browser and go to:")
    print(f"   http://localhost:{port}")
    print("\n" + "="*60 + "\n")

    # Run the app
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == "__main__":
    main()
