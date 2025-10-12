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

```
User Input → Main Chat Agent → (gather requirements) → generate_ppt tool →
PPT Agent → (create HTML files) → return_ppt_result →
Screenshot Capture (Playwright) → PPTX Export (python-pptx) → User
```

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
  - Routes: `/` (home), `/api/chat` (chat endpoint), `/api/download` (PPTX download), `/api/reset` (reset session)
  - Uses Flask sessions to maintain separate chat instances per user
  - Stores uploaded files in `uploads/` directory

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

# Clear generated files (be careful!)
rm -rf slides/*.html screenshots/*.png exports/*.pptx
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

## Code Architecture Notes

### Message Flow in Web Mode
- User sends message via `/api/chat` POST endpoint
- Flask session maintains separate `MainChat` instance per user
- Uploaded files saved to `uploads/` with session-specific subdirectories
- Chat history persists in session until `/api/reset` is called

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
- `agent/ppt_agent.py:139-143` - System prompt specifies exact 1920x1080px dimensions
- `utils/screenshot.py` - Viewport size (currently 1920x1080)
- `utils/export.py` - PPTX slide dimensions (currently 10" × 5.625" for 16:9)

## Recent Improvements

### PPT Agent Prompt Redesign (Latest)
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

- `flask`: Web framework for browser interface
- `anthropic`: Claude API client
- `python-dotenv`: Environment variable management
- `playwright`: Browser automation for screenshots
- `python-pptx`: PowerPoint file generation
- `Pillow`: Image processing

## Environment Variables

```bash
ANTHROPIC_API_KEY=your-api-key-here      # Required: Claude API key
FLASK_PORT=5000                           # Optional: Web server port (default: 5000)
FLASK_DEBUG=True                          # Optional: Debug mode (default: True)
FLASK_SECRET_KEY=random-secret-key        # Optional: Session secret (default: dev key)
```
