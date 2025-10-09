# Installation Instructions

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Step 1: Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

## Step 2: Install Playwright Browsers

Playwright requires browser binaries to be installed separately:

```bash
# Install Playwright browser binaries
playwright install chromium
```

**Note**: This downloads the Chromium browser (~100MB) which is used for screenshot capture.

## Step 3: Set Up Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=your-api-key-here
```

## Step 4: Verify Installation

Test that everything is installed correctly:

```bash
python -c "import anthropic, playwright, pptx; print('✅ All packages installed successfully!')"
```

## Troubleshooting

### Playwright Installation Issues

If `playwright install` fails:

```bash
# Try installing with verbose output
playwright install chromium --verbose

# Or use Python module
python -m playwright install chromium
```

### python-pptx Issues

If you encounter issues with python-pptx:

```bash
# Install with explicit version
pip install python-pptx==1.0.2
```

### Permission Errors

On macOS/Linux, if you get permission errors:

```bash
# Install with user flag
pip install --user -r requirements.txt
```

## Package Details

The following packages will be installed:

- **flask** (3.1.0): Web framework (optional, for future features)
- **anthropic** (0.40.0): Anthropic Claude API client
- **python-dotenv** (1.0.1): Environment variable management
- **playwright** (1.51.0): Browser automation for screenshots
- **python-pptx** (1.0.2): PowerPoint file generation
- **Pillow** (11.0.0): Image processing

## Next Steps

After installation, run:

```bash
python main.py
```

Enjoy creating presentations! 🎨
