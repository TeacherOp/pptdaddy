# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PPT Daddy is an AI-powered presentation generator that creates HTML slides and exports them to PowerPoint format. It features both a web interface and CLI, using a dual-agent architecture with Anthropic's Claude API to collect requirements and generate slides.

### Interface Modes

1. **Web Interface (Recommended)** - Flask application with Jinja templates and Tailwind CSS
   - Browser-based chat interface
   - Drag-and-drop file upload
   - Real-time progress display
   - Download button for PPTX files
   - Entry points: `python app.py` or `python main.py` (choose option 1)

2. **CLI Mode** - Terminal-based interaction
   - Interactive conversation mode
   - Quick generation mode with command-line arguments
   - Entry point: `python main.py` (choose option 2)

## Architecture

### Dual-Agent System

The system uses **two separate Claude instances** that work together:

1. **Main Chat Agent** (`agent/main_chat.py`)
   - Handles user interaction and requirement gathering
   - Asks clarifying questions to understand presentation needs
   - Analyzes uploaded images for brand colors, logo details, and design patterns
   - Has access to web search for current information
   - Calls the PPT Agent when ready to generate slides

2. **PPT AI Agent** (`agent/ppt_agent.py`)
   - Generates HTML slides based on requirements from Main Chat
   - Has file system tools (create_file, update_file, read_file, list_files, create_folder)
   - Uses `tool_choice: {"type": "any"}` to force tool usage on every turn
   - Creates slides with exact 1920x1080px dimensions (16:9 PowerPoint ratio)
   - Calls `return_ppt_result` to mark completion

### Conversation Flow

**High-level flow:**
```
User Input → Main Chat Agent → (gather requirements) → generate_ppt tool →
PPT Agent → (create HTML files) → return_ppt_result →
Screenshot Capture (Playwright) → PPTX Export (python-pptx) → User
```

**Detailed step-by-step interaction:**

1. **User → Main Chat Agent**
   - User sends message (with optional images)
   - Main Chat analyzes images, extracts brand details
   - Main Chat asks clarifying questions (NEVER generates on first message)

2. **Main Chat → PPT Agent** (via `generate_ppt` tool)
   - Main Chat calls `generate_ppt` with parameters:
     - `topic`, `description`, `details`
     - `brand_color_details`, `brand_logo_details`, `brand_guideline_details`
     - `num_slides`
   - PPT Agent receives this as initial system prompt parameters

3. **PPT Agent Execution Loop**
   - PPT Agent MUST use tools on every iteration (`tool_choice: {"type": "any"}`)
   - Creates base-styles.css first
   - Creates individual slide HTML files
   - Calls `return_ppt_result` with slide metadata
   - Tool executor returns: `PPT_GENERATION_COMPLETE: {json_result}`

4. **Main Chat Receives Result**
   - Detects `PPT_GENERATION_COMPLETE:` marker in tool response
   - Extracts JSON result with slide metadata
   - Triggers screenshot capture (Playwright)
   - Triggers PPTX export (python-pptx)
   - Returns completion message to user

**Key insight:** The two agents never directly communicate. Main Chat initiates PPT Agent via tool call, and PPT Agent signals completion via special marker in tool response.

### Key Components

- **Tool Definitions** (`agent/tools.py`)
  - Main Chat tools: `web_search`, `generate_ppt`
  - PPT Agent tools: `create_folder`, `create_file`, `read_file`, `update_file`, `list_files`, `return_ppt_result`

- **Tool Executor** (`agent/tool_executor.py`)
  - Executes file system operations for PPT Agent
  - Creates/updates HTML files in `slides/` directory

- **Screenshot Capture** (`utils/screenshot.py`)
  - Uses Playwright with Chromium browser (headless=False for debugging)
  - Captures 1920x1080px viewport screenshots
  - Saves to `screenshots/` directory

- **PPTX Export** (`utils/export.py`)
  - Uses python-pptx library
  - Creates 10" × 5.625" slides (16:9 ratio)
  - Adds screenshots as full-slide images
  - Saves to `exports/` directory

- **Web Application** (`app.py`)
  - Flask server with session management
  - Handles file uploads (16MB max, supports PNG/JPG/GIF/WEBP)
  - Routes:
    - `/` - Home page (main interface)
    - `/api/chat/stream` - Streaming chat endpoint with real-time progress (RECOMMENDED)
    - `/api/chat` - Legacy non-streaming chat endpoint (fallback)
    - `/api/download` - PPTX file download
    - `/api/reset` - Reset current session
  - Uses Flask sessions to maintain separate chat instances per user
  - Stores uploaded files in `uploads/` directory
  - **Real-time Progress Streaming**: Uses Server-Sent Events (SSE) to stream progress updates during generation

## Development Commands

### Setup and Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (required for screenshots)
playwright install chromium

# Set up environment
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
```

### Running the Application

**Web Interface (Recommended):**
```bash
# Start Flask server
python app.py
# Or via launcher
python main.py  # Choose option 1

# Open browser to http://localhost:5000
```

**CLI Mode:**
```bash
# Interactive terminal mode
python main.py  # Choose option 2

# Quick generation mode
python main.py "Create a Q4 roadmap presentation"
```

### Testing Individual Components

```bash
# Test Playwright installation
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

# Test all dependencies
python3 -c "import anthropic, playwright, pptx; print('All packages OK')"

# Test environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API key loaded' if os.getenv('ANTHROPIC_API_KEY') else 'No API key')"
```

### Debugging

```bash
# View recent slides
ls -lht slides/

# Check screenshot output
ls -lht screenshots/

# Verify PPTX exports
ls -lht exports/
```

### Cleanup Commands

```bash
# Clear all generated files (fresh start)
rm -rf slides/*.html slides/*.css screenshots/*.png exports/*.pptx uploads/*

# Clear only PPTX exports (keep slides and screenshots for debugging)
rm -rf exports/*.pptx

# Clear old uploads (web mode)
rm -rf uploads/*

# Clear everything except base directories
find slides screenshots exports uploads -type f -delete

# Clear session-specific uploads (replace SESSION_ID)
rm -f uploads/SESSION_ID_*
```

## Critical Design Details

### Slide Dimensions and Design Philosophy
- **Exact dimensions**: 1920x1080px (16:9 aspect ratio)
- Use Tailwind classes: `w-[1920px] h-[1080px]` with `overflow-hidden`
- **Height constraint**: All content must fit within 1080px (most critical requirement)
- **Design approach**: Principles-based, not template-based - AI should be creative while respecting constraints
- Always include complete HTML structure (DOCTYPE, head, body)
- Load Tailwind CSS from CDN: `https://cdn.tailwindcss.com`
- Use brand-specified fonts from Google Fonts (or Inter as default)

### PPT Agent Workflow
PPT Agent follows a strict 3-step process:
1. **Create base-styles.css first** - Common styles imported by all slides
2. **Create individual slides** - Each slide imports base-styles.css + custom styles
3. **Call return_ppt_result** - Signal completion with slide metadata

**Important constraints:**
- No animations or interactive elements (screenshots are static)
- No hover effects or JavaScript
- Use Font Awesome icons from CDN: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.1/css/all.min.css`
- Content must fit viewport with no scrollbars
- Healthy spacing on all boundaries to prevent content cutoff

### Image Analysis
When users provide images (logos, screenshots):
- Main Chat analyzes them for brand colors, design patterns, typography
- Extracts hex color codes and design characteristics
- Passes detailed analysis to PPT Agent via `brand_color_details`, `brand_logo_details`, `brand_guideline_details`

### Agent Communication Protocol
- PPT Agent **must** use tools on every iteration (`tool_choice: {"type": "any"}`)
- PPT Agent is given creative freedom but must respect height constraints
- PPT Agent should analyze brand details carefully and use exact brand colors
- PPT Agent signals completion with `return_ppt_result` tool
- Tool executor returns special marker: `PPT_GENERATION_COMPLETE: {json_result}`
- Main Chat detects this marker and extracts final result

### Conversation Philosophy
**CRITICAL**: Main Chat must have a back-and-forth conversation with users BEFORE generating slides:
- NEVER call `generate_ppt` on the first message
- Ask clarifying questions about topic, purpose, audience, and key points
- Wait for user responses before proceeding
- Analyze uploaded images for brand details (colors, logos, design patterns)
- Use `web_search` tool when current information is needed
- Only call `generate_ppt` after gathering comprehensive requirements (typically 2-3+ exchanges)

The Main Chat's role is consultative - it should feel like working with a presentation designer who asks thoughtful questions.

### PPTX Export Pipeline
1. PPT Agent creates HTML files in `slides/`
2. Playwright captures screenshots at 1920x1080px
3. python-pptx creates presentation with 16:9 slides
4. Screenshots are inserted as full-slide images
5. Final PPTX saved to `exports/`

## File Organization

```
slides/          # Generated HTML slides (slide_1.html, slide_2.html, etc.)
screenshots/     # PNG screenshots captured by Playwright
exports/         # Final PPTX files
uploads/         # User-uploaded files (web mode)
templates/       # Jinja templates for web UI
  index.html     # Main web interface
assets/
  logos/         # User-provided logos (CLI mode)
  images/        # User-provided screenshots/images (CLI mode)
```

## API Model

Both agents use: `claude-sonnet-4-5-20250929`
- Main Chat: max_tokens=16000, temperature=0
- PPT Agent: max_tokens=4000, temperature=0, tool_choice={"type": "any"}

## Important Code Patterns

### Progress Callback System
All agents and utilities support optional progress callbacks for real-time updates:

```python
# In agent/ppt_agent.py
class PPTAgent:
    def __init__(self, api_key: str = None, progress_callback=None):
        self.progress_callback = progress_callback

    def _emit_progress(self, event_type: str, data: dict):
        """Emit a progress event if callback is set"""
        if self.progress_callback:
            self.progress_callback(event_type, data)

# Usage in app.py streaming endpoint
def progress_callback(event_type, data):
    """Callback function to receive progress updates"""
    progress_queue.put({'event': event_type, 'data': data})

chat_instance = MainChat(
    api_key=api_key,
    progress_callback=progress_callback
)
```

### Server-Sent Events (SSE) Streaming
```python
# In app.py - /api/chat/stream endpoint
def generate():
    """Generator function for Server-Sent Events"""
    while True:
        try:
            event = progress_queue.get(timeout=0.1)

            if event['event'] == 'done':
                # Send final response
                yield f"data: {json.dumps({'event': 'complete', 'data': {...}})}\n\n"
                break
            else:
                # Stream progress event
                yield f"data: {json.dumps(event)}\n\n"

        except queue.Empty:
            # Keep connection alive
            yield f": keepalive\n\n"

return Response(
    stream_with_context(generate()),
    mimetype='text/event-stream',
    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
)
```

### Frontend Streaming with Fetch API
```javascript
// In templates/index.html
const response = await fetch('/api/chat/stream', {
    method: 'POST',
    body: formData
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = '';

while (true) {
    const {value, done} = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, {stream: true});

    // Process complete lines
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
        if (line.startsWith('data: ')) {
            const data = JSON.parse(line.substring(6));
            handleStreamEvent(data); // Update UI in real-time
        }
    }
}
```

### Reading Images for API
Images must be base64-encoded and included in message content array:

```python
# In agent/main_chat.py
import base64

# Read and encode image
with open(image_path, 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Determine media type
ext = image_path.split('.')[-1].lower()
if ext == 'jpg':
    ext = 'jpeg'

# Add to message content
message_content.append({
    "type": "image",
    "source": {
        "type": "base64",
        "media_type": f"image/{ext}",
        "data": image_data
    }
})
```

### Tool Response Parsing
PPT Agent completion is detected via special marker:

```python
# In agent/main_chat.py - _process_tool_use() method
if "PPT_GENERATION_COMPLETE:" in tool_result:
    # Extract JSON result from marker
    result_json = tool_result.split("PPT_GENERATION_COMPLETE:")[1].strip()
    final_result = json.loads(result_json)

    # Trigger screenshot capture and PPTX export
    capture_screenshots(final_result['slides'])
    export_to_pptx(final_result)

    return final_result
```

### Session-Specific File Handling
```python
# In app.py - chat() route
session_id = session.get('session_id')
unique_filename = f"{session_id}_{secure_filename(file.filename)}"
filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
file.save(filepath)
```

### Preventing Cross-Session File Contamination
```python
# In app.py - chat() route
session_start_time = chat_session.get('session_start_time', 0)

# Only link PPTX files created AFTER this session started
for pptx_path in pptx_files:
    if os.path.getmtime(pptx_path) > session_start_time:
        pptx_file = str(pptx_path)
        chat_session['pptx_file'] = pptx_file
        break
```

## Code Architecture Notes

### Message Flow in Web Mode
- User sends message via `/api/chat` POST endpoint
- Flask session maintains separate `MainChat` instance per user
- Uploaded files saved to `uploads/` with session-specific subdirectories
- Chat history persists in session until `/api/reset` is called

### Session Management in Web Mode
- Each browser session gets a unique UUID stored in Flask session (`session['session_id']`)
- `chat_sessions` dict maintains MainChat instances per session (in-memory storage)
- Each session tracks:
  - `chat`: MainChat instance
  - `messages`: List of conversation messages
  - `pptx_file`: Path to generated PPTX file
  - `session_start_time`: Timestamp when session was created
- PPTX files are only linked to sessions if created AFTER `session_start_time` (prevents cross-session contamination)
- `/api/reset` clears session and removes from `chat_sessions` dict
- **Production note**: Replace in-memory `chat_sessions` with Redis or database for multi-server deployments

### File Upload Handling (Web Mode)
- Uploaded files saved to `uploads/` with format: `{session_id}_{secure_filename}`
- Maximum file size: 16MB (configurable via `app.config['MAX_CONTENT_LENGTH']`)
- Allowed extensions: png, jpg, jpeg, gif, webp (validated by `allowed_file()` function)
- Files are passed to MainChat as file paths (list of strings)
- MainChat reads files and base64-encodes images for Claude API
- Uploaded files persist until server restart or manual cleanup

### Real-Time Progress Streaming (Web Mode)
- **Endpoint**: `/api/chat/stream` (recommended over legacy `/api/chat`)
- **Protocol**: Server-Sent Events (SSE) for one-way server-to-client streaming
- **Implementation**:
  - Uses `queue.Queue()` for thread-safe event communication
  - Runs chat processing in background thread via `threading.Thread`
  - Progress callback function puts events into queue
  - Generator function yields SSE-formatted events to client
  - Keeps connection alive with periodic keepalive messages

**Progress Events Emitted:**
- `generate_ppt_started` - When Main Chat calls generate_ppt tool
- `agent_started` - When PPT Agent initializes
- `iteration` - Each agent iteration (max 30)
- `tool_use` - When agent uses a tool (create_file, update_file, etc.)
- `tool_result` - Result of tool execution
- `export_started` - Beginning of PPTX export process
- `capturing_screenshots` - Starting screenshot capture
- `screenshot_captured` - Each individual slide screenshot (with progress: 1/8, 2/8, etc.)
- `creating_pptx` - Starting PPTX file creation
- `pptx_slide_added` - Each slide added to PPTX (with progress)
- `export_complete` - PPTX export finished
- `complete` - Entire process complete (includes final AI response)
- `error` - Any errors during processing

**Frontend Handling:**
- Uses Fetch API with `response.body.getReader()` for streaming
- Displays progress in expandable panel with color-coded updates
- Auto-scrolls to show latest progress
- Different icons for different event types (🤖 Agent, 📄 Files, 📸 Screenshots, 📊 PPTX)
- Keeps user informed throughout 2-5 minute generation process

### File Naming Convention
- Slides: `slides/slide_1.html`, `slides/slide_2.html`, etc. (sequential numbering)
- Screenshots: `screenshots/slide_1.png`, `screenshots/slide_2.png`, etc.
- PPTX exports: `exports/{presentation_title}.pptx` (spaces replaced with underscores)

### Error Handling
- Tool execution errors are returned as strings starting with "Error:"
- PPT Agent can recover from errors and retry operations
- If max iterations (30) reached, generation fails gracefully
- Main Chat has 10 iteration limit before returning error

## Modifying Agent Behavior

### Changing Main Chat Prompts
Edit `agent/main_chat.py:286` - `_get_system_prompt()` method
- Controls conversation style and requirement gathering
- Emphasizes asking questions before generation
- Defines when to call `generate_ppt` tool

### Changing PPT Agent Prompts
Edit `agent/ppt_agent.py:133` - `_build_system_prompt()` method
- Controls slide generation approach and constraints
- Defines the 3-step workflow (base-styles.css → slides → return)
- Sets design rules and technical constraints

### Adding New Tools
1. Define tool in `agent/tools.py` (either MAIN_CHAT_TOOLS or PPT_AGENT_TOOLS)
2. For PPT Agent tools: Add execution logic to `agent/tool_executor.py:16` in `execute_tool()`
3. For Main Chat tools: Add execution logic to `agent/main_chat.py:196` in `_process_tool_use()`

### Adjusting Slide Dimensions
Change dimensions in multiple places:
- `agent/ppt_agent.py` - System prompt specifies exact 1920x1080px dimensions
- `utils/screenshot.py` - Viewport size (currently 1920x1080)
- `utils/export.py` - PPTX slide dimensions (currently 10" × 5.625" for 16:9)

### Adding New Progress Events
To add new progress tracking points:
1. Call `self._emit_progress(event_type, data)` in agent or utility
2. Add event handler in `templates/index.html` in `handleStreamEvent()` function
3. Choose appropriate icon and color for the event type
4. Update CLAUDE.md to document the new event type

## Recent Improvements

### Real-Time Progress Streaming (Latest - v2)
Implemented Server-Sent Events (SSE) for real-time progress updates during presentation generation:

**What changed:**
1. **Backend**: Added `progress_callback` parameter throughout agent architecture
2. **New Endpoint**: `/api/chat/stream` provides real-time updates via SSE
3. **Frontend**: Beautiful progress panel shows live status updates
4. **UX Enhancement**: Users see exactly what's happening instead of generic "loading" indicator

**Benefits:**
- Users stay informed during 2-5 minute generation process
- Can see which slide is being created/captured in real-time
- Reduces perceived wait time
- Better debugging (errors appear immediately with context)
- Professional UX matching modern web applications

**Events tracked:**
- Agent initialization
- Each tool use (file creation, updates)
- Screenshot capture progress (1/8, 2/8, etc.)
- PPTX assembly progress
- Completion with download link

### PPT Agent Prompt Redesign (v1)
The PPT Agent system prompt has been completely rewritten to prevent content overflow issues:

**Key improvements:**
1. **Exact dimensions specified**: Changed from vague "~1400x800px" to precise "EXACTLY 1920px × 1080px"
2. **Concrete HTML template**: Provides exact structure to copy for every slide
3. **Tailwind CSS enforcement**: Explicitly requires Tailwind classes only, no custom CSS in slides
4. **Overflow prevention checklist**: Mental checklist before creating each slide
5. **Usable area calculation**: Specifies that with p-20 padding, usable area is ~1760px × ~920px
6. **Content limits**: Maximum 5-6 bullet points, max heading size text-6xl, etc.
7. **Example base-styles.css**: Shows exactly what should go in the shared CSS file

**Result:** Eliminates content overflow issues while maintaining creative freedom

## Common Issues

### Agent not creating files
- Ensure `tool_choice: {"type": "any"}` is set in PPT Agent
- Check that system prompt emphasizes immediate tool usage

### Screenshot capture fails
- Verify Playwright is installed: `playwright install chromium`
- Check that HTML files exist in `slides/` directory
- Ensure viewport is set to 1920x1080px

### PPTX export issues
- Ensure `exports/` directory exists (created automatically)
- Verify python-pptx is installed correctly
- Check that screenshots were captured successfully

### Images not analyzed
- Main Chat must extract brand details from images and pass to PPT Agent
- Images should be passed as base64-encoded content in message content array
- File paths like `image:path/to/file.png` are parsed in main.py

## Dependencies

- `flask`: Web framework for browser interface (includes SSE streaming support)
- `anthropic`: Claude API client
- `python-dotenv`: Environment variable management
- `playwright`: Browser automation for screenshots
- `python-pptx`: PowerPoint file generation
- `Pillow`: Image processing

**Note**: No additional dependencies required for streaming - uses built-in Python `queue` and `threading` modules

## Environment Variables

```bash
ANTHROPIC_API_KEY=your-api-key-here      # Required: Claude API key
FLASK_PORT=5000                           # Optional: Web server port (default: 5000)
FLASK_DEBUG=True                          # Optional: Debug mode (default: True)
FLASK_SECRET_KEY=random-secret-key        # Optional: Session secret (default: dev key)
```

## Testing

**IMPORTANT**: Per project policy, **do not run tests automatically**. The user will run tests manually.

### Testing Workflow
1. Make code changes as requested
2. Inform user that changes are complete
3. User runs tests and reports results
4. Fix any issues if tests fail

### Manual Testing Commands (for user reference)

**Component testing:**
```bash
# Test Playwright installation
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

# Test all dependencies
python3 -c "import anthropic, playwright, pptx; print('All packages OK')"

# Test environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API key loaded' if os.getenv('ANTHROPIC_API_KEY') else 'No API key')"
```

**Application testing:**
```bash
# Test web server (manual - open browser to http://localhost:5000)
python app.py

# Test CLI mode (manual - follow prompts)
python main.py  # Choose option 2

# Quick test with command-line argument
python main.py "Test presentation about Python"
```

**Integration testing:**
```bash
# Full end-to-end test (web mode)
# 1. Start server: python app.py
# 2. Open browser to http://localhost:5000
# 3. Create a presentation through chat
# 4. Verify PPTX download works
# 5. Check exports/ directory for .pptx file

# Full end-to-end test (CLI mode)
# 1. Run: python main.py
# 2. Choose option 2 (Terminal Interactive Mode)
# 3. Create a presentation through terminal prompts
# 4. Verify files in slides/, screenshots/, exports/
```
