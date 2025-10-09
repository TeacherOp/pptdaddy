# 🎨 PPT Daddy - AI-Powered Presentation Generator

Generate stunning PowerPoint presentations using AI! Just describe what you want, and PPT Daddy creates beautiful HTML slides and exports them to PPTX format - completely free and open source.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red)](https://github.com/yourusername/pptdaddy)

---

## ✨ Features

- 🤖 **AI-Powered Generation** - Uses Anthropic Claude to create presentations
- 🎨 **Custom Branding** - Supports brand colors, logos, and guidelines
- 📸 **Image Analysis** - Analyzes your logo and screenshots for brand consistency
- 🌐 **Web Search** - Finds current information for your presentations
- 💼 **Professional Templates** - Beautiful, modern slide designs using Tailwind CSS
- 📊 **PPTX Export** - Automatically exports to PowerPoint format
- 🖼️ **HTML Slides** - View slides directly in your browser (1920x1080px)
- 🆓 **100% Free & Open Source** - No limits, no paywalls

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/pptdaddy.git
cd pptdaddy
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers** (for PPTX export)
```bash
playwright install chromium
```

5. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Run

```bash
python main.py
```

That's it! 🎉

---

## 📖 Usage

### Interactive Mode (Recommended)

```bash
python main.py
```

The AI will guide you through creating your presentation:

```
You: I need a pitch deck for my AI startup called "DataFlow"

AI: Great! I'd love to help you create a pitch deck for DataFlow.
    What does DataFlow do and what slides do you want to include?

You: We help companies automate data pipelines. Include: problem,
     solution, market size, our tech, team, and ask. Use colors
     #2563EB and #F59E0B

AI: Perfect! Let me generate your pitch deck...

✅ Successfully generated presentation!
   Slide count: 8
   📊 PPTX File: exports/DataFlow_Pitch_Deck.pptx
   You can open this file in PowerPoint or Keynote!
```

### Quick Mode

```bash
python main.py "Create a Q4 roadmap presentation"
```

### With Images

Place your logo and screenshots in the `assets/` folder, then:

```
You: Create a presentation for my startup image:assets/logos/logo.png image:assets/images/app.jpg
```

The AI will analyze the images for brand colors and styling!

---

## 🎨 How It Works

1. **Main AI Chat** - Collects presentation requirements from you
   - Asks clarifying questions
   - Analyzes images for branding
   - Uses web search for current data

2. **PPT AI Agent** - Generates HTML slides
   - Creates beautiful Tailwind CSS slides (1920x1080px)
   - Follows your brand guidelines
   - Ensures consistent design

3. **Auto Export** - Creates PPTX file
   - Screenshots HTML slides using Playwright
   - Exports to PowerPoint format
   - Saves to `exports/` folder

```
User Input → Main AI Chat → PPT AI Agent → HTML Slides → Screenshots → PPTX Export
```

---

## 📁 Project Structure

```
pptdaddy/
├── main.py                 # Entry point
├── agent/
│   ├── main_chat.py       # Main AI chat interface
│   ├── ppt_agent.py       # PPT generation agent
│   ├── tools.py           # Tool definitions
│   └── tool_executor.py   # Tool execution
├── utils/
│   ├── screenshot.py      # Screenshot capture (Playwright)
│   └── export.py          # PPTX export (python-pptx)
├── slides/                # Generated HTML slides
├── exports/               # Generated PPTX files
├── screenshots/           # Slide screenshots
├── assets/                # Your brand assets
│   ├── logos/
│   └── images/
└── requirements.txt
```

---

## 🛠️ Configuration

### Environment Variables

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=your-api-key-here
FLASK_PORT=5000
FLASK_DEBUG=True
```

### Slide Dimensions

- **Default**: 1920x1080px (16:9 standard PowerPoint ratio)
- **Format**: HTML with Tailwind CSS
- **Export**: High-quality PNG screenshots → PPTX

---

## 📝 Examples

### Example 1: Startup Pitch Deck
```
Topic: "SaaS Product Launch"
Description: "Pitch deck for Series A funding"
Details: "Problem, Solution, Market Size, Business Model, Traction, Team, Ask"
Brand Colors: "#1E40AF, #F59E0B"
```

### Example 2: Corporate Presentation
```
Topic: "Q4 Business Review"
Description: "Executive summary for stakeholders"
Details: "Revenue, KPIs, Product launches, 2025 goals"
Brand: "Professional, use company logo"
```

### Example 3: Educational Content
```
Topic: "Introduction to AI"
Description: "Workshop for students"
Details: "What is AI, Types of AI, Applications, Future trends"
Style: "Friendly, visual, easy to understand"
```

---

## 🎯 Tips for Best Results

1. **Be Specific** - The more details you provide, the better the output
2. **Provide Brand Assets** - Upload logos and screenshots for consistent branding
3. **Use Hex Colors** - Provide exact color codes (#HEXCODE format)
4. **Define Tone** - Specify if you want professional, casual, technical, etc.
5. **Review HTML First** - Check slides in browser before using PPTX

---

## 🐛 Troubleshooting

### Common Issues

**"ANTHROPIC_API_KEY not found"**
- Make sure you created `.env` file with your API key

**"Playwright browser not found"**
```bash
playwright install chromium
```

**Slides look weird in browser**
- Make sure you're viewing at 100% zoom
- Use a modern browser (Chrome, Firefox, Safari)

**PPTX export fails**
- Check that `exports/` directory exists
- Ensure Playwright is installed correctly
- Run `playwright install chromium` again

**Agent not creating files**
- This is now fixed with `tool_choice` parameter
- Agent is forced to use tools on every turn

---

## 📚 Documentation

- [Installation Guide](INSTALL.md) - Detailed setup instructions
- [Anthropic API Guide](ANTHROPIC_API_GUIDE.md) - Complete guide to Anthropic's API
- [Architecture Plan](PPT_GENERATOR_MVP_PLAN.md) - Detailed system design

---

## 🤝 Contributing

Contributions are welcome! This is a free and open-source project.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - free to use, modify, and distribute!

---

## 🙏 Acknowledgments

- Built with [Claude](https://www.anthropic.com/claude) by Anthropic
- UI powered by [Tailwind CSS](https://tailwindcss.com/)
- Screenshot capture by [Playwright](https://playwright.dev/)
- PPT export by [python-pptx](https://python-pptx.readthedocs.io/)

---

## 🌟 Star Us!

If you find PPT Daddy useful, please consider giving it a star ⭐️

---

## 🔮 Future Roadmap

- [ ] PDF export option
- [ ] Web UI interface
- [ ] Template marketplace
- [ ] Collaboration features
- [ ] Cloud hosting option
- [ ] More slide templates
- [ ] Animation support

---

<div align="center">

### Built with ❤️ by the [ReplyDaddy.com](https://replydaddy.com) team

**Free & Open Source Forever**

[Report Bug](https://github.com/yourusername/pptdaddy/issues) · [Request Feature](https://github.com/yourusername/pptdaddy/issues) · [Documentation](ANTHROPIC_API_GUIDE.md)

Made possible by **Anthropic Claude** 🤖

</div>
