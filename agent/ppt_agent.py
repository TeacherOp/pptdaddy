"""
PPT AI Agent - Generates HTML slides using AI and file creation tools
"""

import anthropic
import os
from typing import Dict, List
from .tools import PPT_AGENT_TOOLS
from .tool_executor import PPTToolExecutor
from utils.screenshot import capture_slide_screenshots
from utils.export import create_pptx_from_screenshots


class PPTAgent:
    """AI Agent that generates PowerPoint slides as HTML files"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.tool_executor = PPTToolExecutor()
        self.messages = []

    def generate_presentation(self, ppt_data: Dict) -> Dict:
        """
        Generate a presentation based on the provided data

        Args:
            ppt_data: Dictionary containing:
                - ppt_topic: str
                - ppt_description: str
                - ppt_details: str
                - ppt_data: str (optional)
                - brand_logo_details: str (optional)
                - brand_guideline_details: str (optional)
                - brand_color_details: str (optional)

        Returns:
            Result dictionary with success status and slide information
        """

        # Build the initial prompt for the PPT Agent
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(ppt_data)

        # Initialize conversation
        self.messages = [
            {"role": "user", "content": user_prompt}
        ]

        print("\n" + "="*60)
        print("🤖 PPT AI Agent Started")
        print("="*60)
        print(f"\nGenerating presentation: {ppt_data['ppt_topic']}\n")

        # Agent loop - continues until return_ppt_result is called
        max_iterations = 30
        iteration = 0
        final_result = None

        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")

            # Make API request
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
                system=system_prompt,
                tools=PPT_AGENT_TOOLS,
                tool_choice={"type": "any"},  # Force the model to use a tool
                messages=self.messages
            )

            # Check if agent wants to use tools
            if response.stop_reason == "tool_use":
                # Process tool use
                tool_results = self._process_tool_use(response)

                # Check if agent returned final result
                if self._is_generation_complete(tool_results):
                    final_result = self._extract_final_result(tool_results)

                    # Export to PPTX if generation was successful
                    if final_result.get("success") and final_result.get("slide_files"):
                        final_result = self._export_to_pptx(final_result, ppt_data.get('ppt_topic', 'Presentation'))

                    break

                # Add assistant message and tool results to conversation
                self.messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                self.messages.append({
                    "role": "user",
                    "content": tool_results
                })

            else:
                # Agent finished without using tools (shouldn't happen in normal flow)
                print("\n⚠️  Agent finished without calling return_ppt_result")
                response_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        response_text += block.text

                final_result = {
                    "success": False,
                    "message": f"Agent stopped unexpectedly: {response_text}",
                    "slide_count": 0,
                    "slide_files": []
                }
                break

        if iteration >= max_iterations:
            print("\n⚠️  Max iterations reached")
            final_result = {
                "success": False,
                "message": "Max iterations reached without completion",
                "slide_count": 0,
                "slide_files": []
            }

        print("\n" + "="*60)
        print("✅ PPT AI Agent Finished")
        print("="*60)
        print(f"Result: {final_result}\n")

        return final_result

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the PPT Agent"""
        return """You are a specialized AI agent that generates PowerPoint presentations as HTML files.

Your task is to create beautiful, professional HTML slides based on user requirements. Always use the available tools to complete your task and only and only use the available tools to create a file and relvant code in it, once all files are created / updated / use the return result tool to notify us that generation process is completed.

CRITICAL: You MUST use your tools to create files. DO NOT just describe what you will do - actually DO it using the create_file tool immediately!

=== SLIDE DIMENSIONS (16:9 ASPECT RATIO) ===
- Width: 1920px, Height: 1080px (Standard PowerPoint size)
- Use these EXACT dimensions in every slide
- Container div: class="w-[1920px] h-[1080px]"
- You have 1920x1080 pixels of space - use it intelligently!
- Always follow similar templates and designs for each slide of a project to maintain consistency
=== Example HTML STRUCTURE TEMPLATE ===
Use this example structure for every slide if needed, or use your own structure as long as the size branding etc is consistent across all slides generated for a project:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f3f4f6;
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body>
    <div class="w-[1920px] h-[1080px] bg-white shadow-2xl overflow-hidden">
        <!-- Your slide content here -->
    </div>
</body>
</html>
```

=== TAILWIND CSS GUIDELINES ===

1. **Spacing & Layout**:
   - Use consistent padding: p-8, p-10, p-12 for slide padding
   - Use space-y-4, space-y-6 for vertical spacing between elements
   - Use gap-4, gap-6 for grid/flex gaps
   - Center content with: flex items-center justify-center

2. **Typography**:
   - Headings: text-4xl, text-5xl, text-6xl
   - Body text: text-lg, text-xl, text-2xl
   - Font weights: font-normal, font-semibold, font-bold
   - Line height: leading-tight, leading-snug, leading-relaxed
   - Use Inter font (loaded via Google Fonts)

3. **Colors**:
   - Use brand colors when provided (e.g., bg-[#146eb4])
   - Text colors: text-gray-900, text-gray-700, text-white
   - Backgrounds: bg-white, bg-gray-50, bg-gradient-to-br

4. **Components**:
   - Buttons: px-6 py-3 rounded-lg font-semibold
   - Cards: rounded-xl shadow-lg p-6
   - Lists: space-y-3, flex items-start
   - Icons: Use Unicode symbols (●, ✓, →, etc.)

=== COMMON SLIDE PATTERNS ===

**Title Slide**:
```html
<div class="w-[1920px] h-[1080px] bg-gradient-to-br from-[BRAND_COLOR] to-[DARKER_SHADE] flex flex-col items-center justify-center text-white p-16">
    <h1 class="text-8xl font-bold mb-6 text-center">Title Here</h1>
    <p class="text-4xl text-center opacity-90">Subtitle here</p>
</div>
```

**Content Slide**:
```html
<div class="w-[1920px] h-[1080px] bg-white p-16 flex flex-col">
    <h2 class="text-6xl font-bold text-gray-900 mb-12">Heading</h2>
    <ul class="space-y-6 text-3xl text-gray-700">
        <li class="flex items-start gap-4">
            <span class="text-[BRAND_COLOR] text-4xl">●</span>
            <span>Point one</span>
        </li>
        <!-- Add as many points as needed based on content -->
    </ul>
</div>
```

**Two Column Slide**:
```html
<div class="w-[1920px] h-[1080px] bg-white p-16 flex flex-col">
    <h2 class="text-6xl font-bold text-gray-900 mb-12">Heading</h2>
    <div class="grid grid-cols-2 gap-12 flex-1">
        <div>Left content</div>
        <div>Right content</div>
    </div>
</div>
```

=== DESIGN QUALITY CHECKLIST ===
✓ All text is readable (good contrast)
✓ Consistent padding and margins throughout
✓ Brand colors used appropriately
✓ Content fits within 1920x1080px (use overflow-hidden if needed)
✓ Professional typography hierarchy
✓ Adequate white space
✓ Aligned elements (not misaligned)
✓ Utilize the available space dynamically based on content

=== MANDATORY WORKFLOW ===
Step 1: Create 'slides' folder (if needed)
Step 2: IMMEDIATELY create slide_1.html using the exact HTML structure
Step 3: Create each subsequent slide (slide_2.html, slide_3.html, etc.)
Step 4: Call return_ppt_result when ALL slides are done

DO NOT just plan - CREATE FILES NOW using create_file tool!

=== BRAND CUSTOMIZATION ===
- Replace [BRAND_COLOR] with actual hex color provided
- Use brand fonts if specified
- Follow brand tone in content
- Include logo path if provided (e.g., <img src="../assets/logos/logo.png">)

START CREATING slide_1.html RIGHT NOW!
"""

    def _build_user_prompt(self, ppt_data: Dict) -> str:
        """Build the user prompt with PPT requirements"""

        prompt = f"""Please generate a PowerPoint presentation with the following details:

**Topic**: {ppt_data['ppt_topic']}

**Description**: {ppt_data['ppt_description']}

**Details**: {ppt_data['ppt_details']}
"""

        # Add optional data
        if ppt_data.get('ppt_data'):
            prompt += f"\n**Data/Statistics**: {ppt_data['ppt_data']}\n"

        if ppt_data.get('brand_color_details'):
            prompt += f"\n**Brand Colors**: {ppt_data['brand_color_details']}\n"

        if ppt_data.get('brand_logo_details'):
            prompt += f"\n**Logo Details**: {ppt_data['brand_logo_details']}\n"

        if ppt_data.get('brand_guideline_details'):
            prompt += f"\n**Brand Guidelines**: {ppt_data['brand_guideline_details']}\n"

        prompt += """
Please create professional HTML slides for this presentation. Use your tools to:
1. Create the slides directory if needed
2. Generate each slide as an HTML file
3. Return the final result with all slide files

Start now!
"""

        return prompt

    def _process_tool_use(self, response) -> List[Dict]:
        """Process tool use requests from the agent"""

        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                print(f"\n🔧 Tool: {tool_name}")
                print(f"   Input: {tool_input}")

                # Execute the tool
                result = self.tool_executor.execute_tool(tool_name, tool_input)

                print(f"   Result: {result[:200]}..." if len(result) > 200 else f"   Result: {result}")

                # Check if it's an error
                is_error = result.startswith("Error:")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": is_error
                })

        return tool_results

    def _is_generation_complete(self, tool_results: List[Dict]) -> bool:
        """Check if the agent called return_ppt_result"""
        for result in tool_results:
            if "PPT_GENERATION_COMPLETE" in result.get("content", ""):
                return True
        return False

    def _extract_final_result(self, tool_results: List[Dict]) -> Dict:
        """Extract the final result from return_ppt_result"""
        import json

        for result in tool_results:
            content = result.get("content", "")
            if "PPT_GENERATION_COMPLETE" in content:
                # Extract JSON part
                json_part = content.split("PPT_GENERATION_COMPLETE:")[1].strip()
                return json.loads(json_part)

        return {
            "success": False,
            "message": "Could not extract final result",
            "slide_count": 0,
            "slide_files": []
        }

    def _export_to_pptx(self, result: Dict, presentation_title: str) -> Dict:
        """
        Export HTML slides to PPTX

        Args:
            result: Result dictionary from return_ppt_result
            presentation_title: Title of the presentation

        Returns:
            Updated result dictionary with PPTX file path
        """
        try:
            print("\n" + "="*60)
            print("📤 Exporting to PPTX")
            print("="*60)

            slide_files = result["slide_files"]

            # Capture screenshots
            screenshots = capture_slide_screenshots(slide_files)

            if not screenshots:
                print("⚠️  No screenshots captured, skipping PPTX export")
                return result

            # Create PPTX
            pptx_file = create_pptx_from_screenshots(
                screenshots,
                output_file=f"exports/{presentation_title.replace(' ', '_')}.pptx",
                presentation_title=presentation_title
            )

            # Add PPTX file to result
            result["pptx_file"] = pptx_file
            result["screenshots"] = screenshots

            return result

        except Exception as e:
            print(f"❌ Error exporting to PPTX: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return original result even if export fails
            return result
