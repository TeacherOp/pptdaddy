#!/usr/bin/env python3
"""
PPT Daddy - AI-Powered Presentation Generator
Main entry point for the application
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agent.main_chat import MainChat

# Load environment variables
load_dotenv()


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*60)
    print("🎨 PPT DADDY - AI-Powered Presentation Generator")
    print("="*60)
    print("\nWelcome! I'll help you create amazing presentations.")
    print("Just tell me what you want to present, and I'll generate")
    print("beautiful HTML slides for you.\n")
    print("Features:")
    print("  • AI-powered slide generation")
    print("  • Custom brand colors and styling")
    print("  • Image analysis for brand guidelines")
    print("  • Web search for current information")
    print("\n" + "="*60 + "\n")


def print_instructions():
    """Print usage instructions"""
    print("\n💡 How to use:")
    print("   1. Tell me about your presentation topic")
    print("   2. Provide any brand details (colors, logo, guidelines)")
    print("   3. I'll generate HTML slides in the 'slides/' folder")
    print("   4. Open the HTML files directly in your browser!")
    print("\n📝 Example topics:")
    print("   - 'Create a Q4 product roadmap presentation'")
    print("   - 'I need a pitch deck for my startup'")
    print("   - 'Make slides about climate change for students'")
    print("\n💬 Special commands:")
    print("   - Type 'quit' or 'exit' to end the conversation")
    print("   - Type 'help' for these instructions again")
    print("\n" + "-"*60 + "\n")


def interactive_mode():
    """Run in interactive chat mode"""

    print_banner()
    print_instructions()

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("   Please set it in your .env file")
        return

    # Ensure slides directory exists
    Path("slides").mkdir(exist_ok=True)

    # Initialize the main chat
    chat = MainChat(api_key=api_key)

    # Get initial message from user
    print("Tell me about the presentation you want to create:")
    print("(You can also provide image paths for brand analysis)")
    print("\nYour request: ", end="")

    initial_message = input().strip()

    if not initial_message or initial_message.lower() in ['quit', 'exit']:
        print("\n👋 Goodbye!")
        return

    if initial_message.lower() == 'help':
        print_instructions()
        print("\nYour request: ", end="")
        initial_message = input().strip()

    # Check if user provided image paths
    images = None
    if "image:" in initial_message.lower() or ".png" in initial_message or ".jpg" in initial_message:
        print("\n📸 Detecting images in your message...")
        # Extract image paths (simple parsing for MVP)
        # User should format like: "Create a presentation for my startup image:logo.png image:screenshot.jpg"
        parts = initial_message.split()
        images = [p.replace("image:", "") for p in parts if p.startswith("image:") or p.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]

        if images:
            print(f"   Found {len(images)} image(s): {', '.join(images)}")
            # Remove image references from message
            for img in images:
                initial_message = initial_message.replace(f"image:{img}", "").replace(img, "")
            initial_message = " ".join(initial_message.split())

    # Start the conversation
    try:
        chat.start_conversation(initial_message, images)

        # Continue conversation loop
        while True:
            print("\n" + "-"*60)
            print("\nContinue the conversation (or 'quit' to exit):")
            print("You: ", end="")

            user_input = input().strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for using PPT Daddy! Goodbye!")
                break

            if user_input.lower() == 'help':
                print_instructions()
                continue

            # Check for images again
            images = None
            if "image:" in user_input.lower() or any(ext in user_input for ext in ['.png', '.jpg', '.jpeg']):
                parts = user_input.split()
                images = [p.replace("image:", "") for p in parts if p.startswith("image:") or p.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]

                if images:
                    print(f"\n📸 Found {len(images)} image(s): {', '.join(images)}")
                    for img in images:
                        user_input = user_input.replace(f"image:{img}", "").replace(img, "")
                    user_input = " ".join(user_input.split())

            # Send message
            chat.send_message(user_input, images)

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


def quick_generate_mode(topic: str):
    """Quick generation mode with just a topic"""

    print_banner()
    print(f"🚀 Quick Generate Mode: {topic}\n")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found")
        return

    Path("slides").mkdir(exist_ok=True)

    chat = MainChat(api_key=api_key)

    try:
        chat.start_conversation(f"Create a presentation about: {topic}")
        print("\n✅ Done! Check the 'slides/' folder for your presentation.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def web_mode():
    """Launch the web interface"""
    from app import main as web_main
    web_main()


def main():
    """Main entry point"""

    if len(sys.argv) > 1:
        # Check for web mode flag
        if sys.argv[1] in ['--web', '-w', 'web']:
            web_mode()
        else:
            # Quick mode with topic from command line
            topic = " ".join(sys.argv[1:])
            quick_generate_mode(topic)
    else:
        # Default to web mode (can change to interactive_mode() if preferred)
        print("\n" + "="*60)
        print("🎨 PPT DADDY - AI-Powered Presentation Generator")
        print("="*60)
        print("\nChoose a mode:")
        print("  1. Web Interface (Recommended)")
        print("  2. Terminal Interactive Mode")
        print("\nEnter your choice (1 or 2): ", end="")

        try:
            choice = input().strip()
            if choice == "1":
                web_mode()
            elif choice == "2":
                interactive_mode()
            else:
                print("Invalid choice. Launching web interface...")
                web_mode()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    main()
