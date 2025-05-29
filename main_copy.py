from crewai import Agent, Task, Crew, LLM
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json
import re
import time

# Load environment variables
load_dotenv()

# Configuration
INPUT_SVG_FILE = "input.svg"
OUTPUT_SVG_FILE = "output.svg"

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Please set GOOGLE_API_KEY in .env file")
    exit(1)

# Initialize LLM using CrewAI's native LLM class
llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.3,
    api_key=api_key
)

def load_input_svg():
    """Load or create input SVG file"""
    try:
        with open(INPUT_SVG_FILE, 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Create assignment example SVG
        default_svg = '''<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
                        <rect x="50" y="50" width="200" height="100" fill="red"/>
                        </svg>'''
        with open(INPUT_SVG_FILE, 'w') as f:
            f.write(default_svg)
            print(f" Created {INPUT_SVG_FILE}")
        return default_svg

def save_output_svg(svg_content):
    """Save output SVG file"""
    with open(OUTPUT_SVG_FILE, 'w') as f:
        f.write(svg_content)
    print(f"Saved {OUTPUT_SVG_FILE}")

def break_instructions_smart(user_prompt):
    """Break instructions intelligently - keeping complete gradient specs together"""
    
    few_shot_prompt = f"""
Break down complex instructions into complete, actionable gradient operations. Each instruction should contain:
- Target element identification (by color, tag, position, etc.)
- Complete gradient specification (type, direction, colors)
- All necessary details for one complete gradient operation

Examples:

Input: "Change the red rectangle to have a vertical gradient from #ff0000 to #0000ff"
Output: ["Change the red rectangle to have a vertical gradient from #ff0000 to #0000ff"]

Input: "Make the circle green, and give the rectangle a blue-yellow gradient"
Output: ["Make the circle green", "Give the rectangle a blue-yellow gradient"]

Input: "Add a vertical red-to-blue gradient to the red rectangle and make the circle have a radial white-to-black gradient"
Output: ["Add a vertical red-to-blue gradient to the red rectangle", "Make the circle have a radial white-to-black gradient"]

Input: "Give all rectangles sunset gradients"
Output: ["Give all rectangles sunset gradients"]

Now break down this instruction (keep complete gradient specs together):
Input: "{user_prompt}"
Output: """

    try:
        # Use LLM directly for few-shot prompting
        response = llm.call([{"role": "user", "content": few_shot_prompt}])
        
        # Extract JSON array from response
        response_text = str(response)
        print(response_text)
        
        # Try to find JSON array in the response
        if '[' in response_text and ']' in response_text:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            json_str = response_text[start:end]
            instructions = json.loads(json_str)
            return instructions
        else:
            # Fallback: try to parse as simple list
            lines = response_text.strip().split('\n')
            instructions = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('[') and not line.startswith(']'):
                    # Remove quotes and clean up
                    line = line.strip('"').strip("'").strip(',')
                    if line and len(line) > 10:  # Only meaningful instructions
                        instructions.append(line)
            return instructions if instructions else [user_prompt]
            
    except Exception as e:
        print(f" Few-shot parsing failed: {e}")
        return [user_prompt]

def create_3_agent_crew():
    """Create the 3-agent crew that will be reused"""
    
    # Agent 1: Gradient Parser Agent
    gradient_parser = Agent(
        role='Gradient Parser Agent',
        goal='Extract gradient type (linear/radial), direction, start and end colors from user prompt',
        backstory='''You are an expert at parsing natural language instructions for SVG gradients. 
        You extract:
        - Gradient type: linear or radial
        - Direction: vertical, horizontal, diagonal (for linear gradients)
        - Start color: hex code or color name
        - End color: hex code or color name
        - Target element: which element to modify (by color, tag, etc.)
        
        You always provide structured, precise gradient specifications in JSON format.
        For simple color changes (no gradient), you indicate gradient_type as "none".''',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Agent 2: SVG Modifier Agent
    svg_modifier = Agent(
        role='SVG Modifier Agent',
        goal='Insert <defs> block and update element fill attributes with gradients',
        backstory='''You are a skilled SVG developer who modifies SVG files by:
        1. Adding gradient definitions to <defs> blocks
        2. Creating appropriate linearGradient or radialGradient elements
        3. Generating unique gradient IDs
        4. Updating target element fill attributes to reference gradients
        5. Preserving all existing SVG structure
        
        You ensure proper coordinate systems, gradient directions, and element targeting.
        You always produce valid, well-formed SVG code.''',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Agent 3: Integrity Checker Agent
    integrity_checker = Agent(
        role='Integrity Checker Agent',
        goal='Ensure valid SVG syntax and check for missing references like id',
        backstory='''You are a meticulous quality assurance specialist for SVG code.
        You validate XML syntax, gradient definitions, element references, and overall structure.
        You fix any issues to ensure the final SVG is valid and renders correctly.''',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return gradient_parser, svg_modifier, integrity_checker

def process_single_instruction_with_retry(instruction, current_svg, gradient_parser, svg_modifier, integrity_checker, max_retries=3):
    """Process a single instruction with retry logic for rate limiting"""
    
    for attempt in range(max_retries):
        try:
            return process_single_instruction(instruction, current_svg, gradient_parser, svg_modifier, integrity_checker)
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                wait_time = (attempt + 1) * 20  # 20, 40, 60 seconds
                print(f" Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    print(" Max retries reached. Skipping this instruction.")
                    return current_svg
            else:
                print(f" Error processing instruction: {e}")
                return current_svg
    
    return current_svg

def process_single_instruction(instruction, current_svg, gradient_parser, svg_modifier, integrity_checker):
    """Process a single instruction using the 3-agent crew"""
    
    print(f"\n Processing: {instruction}")
    print("-" * 50)
    
    # Task 1: Parse gradient specifications
    parse_task = Task(
        description=f'''
        Parse this gradient instruction: "{instruction}"
        
        Extract the following information:
        1. Gradient type: "linear", "radial", or "none" (for solid colors)
        2. Direction: "vertical", "horizontal", "diagonal" (for linear gradients)
        3. Start color: hex code or color name
        4. End color: hex code or color name (if gradient)
        5. Target element: description of which element to modify
        
        Examples:
        - "Change the red rectangle to vertical gradient from #ff0000 to #0000ff"
          → gradient_type: "linear", direction: "vertical", start_color: "#ff0000", end_color: "#0000ff", target_element: "red rectangle"
        - "Make the circle green"
          → gradient_type: "none", start_color: "green", target_element: "circle"
        - "Add radial gradient from white to black to the blue circle"
          → gradient_type: "radial", start_color: "white", end_color: "black", target_element: "blue circle"
        
        Return JSON object with these fields:
        {{
            "gradient_type": "linear|radial|none",
            "direction": "vertical|horizontal|diagonal",
            "start_color": "color",
            "end_color": "color",
            "target_element": "description"
        }}
        ''',
        expected_output='JSON object with parsed gradient specifications',
        agent=gradient_parser
    )
    
    # Task 2: Modify SVG
    modify_task = Task(
        description=f'''
        Modify this SVG based on the parsed configuration from the previous task:
        
        Current SVG:
        {current_svg}
        
        Instructions:
        1. If gradient_type is "linear": Create linearGradient in <defs> section with proper coordinates
        2. If gradient_type is "radial": Create radialGradient in <defs> section
        3. If gradient_type is "none": Just update fill attribute with solid color
        4. Generate unique gradient ID (e.g., "grad1", "grad2", etc.)
        5. Set appropriate coordinates based on direction:
           - vertical: x1="0%" y1="0%" x2="0%" y2="100%"
           - horizontal: x1="0%" y1="0%" x2="100%" y2="0%"
           - diagonal: x1="0%" y1="0%" x2="100%" y2="100%"
        6. Create proper stop elements with offset and style attributes
        7. Update target element's fill attribute to reference gradient: fill="url(#gradientId)"
        8. Preserve all other elements unchanged
        
        Return complete modified SVG code.
        ''',
        expected_output='Complete modified SVG code',
        agent=svg_modifier,
        context=[parse_task]
    )
    
    # Task 3: Validate and clean
    validate_task = Task(
        description=f'''
        Validate the modified SVG from the previous task:
        
        Check for:
        1. Valid XML syntax
        2. Proper gradient definitions in <defs>
        3. Correct element references to gradient IDs
        4. No missing or broken references
        5. Well-formed SVG structure
        6. Proper stop elements with offset and style attributes
        
        Fix any issues and return the final validated SVG.
        ''',
        expected_output='Final validated SVG code',
        agent=integrity_checker,
        context=[modify_task]
    )
    
    # Create crew for this instruction
    crew = Crew(
        agents=[gradient_parser, svg_modifier, integrity_checker],
        tasks=[parse_task, modify_task, validate_task],
        verbose=True
    )
    
    # Execute the crew
    result = crew.kickoff()
    
    # Extract clean SVG from result
    final_svg = str(result)
    if '<svg' in final_svg and '</svg>' in final_svg:
        start_idx = final_svg.find('<svg')
        end_idx = final_svg.find('</svg>') + 6
        final_svg = final_svg[start_idx:end_idx]
    
    return final_svg

def main():    
    # Load input SVG
    original_svg = load_input_svg()
    
    # Get user input
    user_prompt = input(" Enter your gradient instruction: ").strip()
    if not user_prompt:
        user_prompt = "Change the red rectangle to have a vertical gradient from #ff0000 to #0000ff"
        print(f"Using default: {user_prompt}")
    
    print(f"\n USER PROMPT: \"{user_prompt}\"")
    print(f"\n BEFORE - Original SVG:")
    print(original_svg)
    
    # Step 1: Break instructions using few-shot prompting
    print(f"\n STEP 1: Breaking down instructions (keeping complete gradient specs together)")
    simple_instructions = break_instructions_smart(user_prompt)
    
    print(f" Broken down into {len(simple_instructions)} complete instructions:")
    for i, instruction in enumerate(simple_instructions, 1):
        print(f"   {i}. {instruction}")
    
    # Step 2: Create the 3-agent crew (reused for each instruction)
    print(f"\n STEP 2: Creating 3-agent crew")
    gradient_parser, svg_modifier, integrity_checker = create_3_agent_crew()
    print(" Agents created: Gradient Parser → SVG Modifier → Integrity Checker")
    
    # Step 3: Process each instruction with the crew
    print(f"\n STEP 3: Processing each instruction with 3-agent crew")
    current_svg = original_svg
    
    for i, instruction in enumerate(simple_instructions, 1):
        print(f"\n{'='*60}")
        print(f" INSTRUCTION {i}/{len(simple_instructions)}")
        print(f"{'='*60}")
        
        current_svg = process_single_instruction_with_retry(
            instruction, current_svg, gradient_parser, svg_modifier, integrity_checker
        )
        
        print(f" Instruction {i} completed")
    
    # Save final result
    save_output_svg(current_svg)
    
    # Display final results
    print(f"\n WORKFLOW COMPLETED!")
    print("="*60)
    print(f"\n SUMMARY:")
    print(f"    User Prompt: {user_prompt}")
    print(f"    Instructions Processed: {len(simple_instructions)}")
    print(f"    Agents Used: Gradient Parser → SVG Modifier → Integrity Checker")
    
    print(f"\n AFTER - Final SVG:")
    print(current_svg)

if __name__ == "__main__":
    main() 