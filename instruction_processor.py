import json
import time
from crewai import Task, Crew
from agents import create_llm

def break_instructions_smart(user_prompt):
    """Break instructions intelligently - keeping complete gradient specs together"""
    llm = create_llm()
    
    print("\n=== INSTRUCTION BREAKDOWN PROCESS ===")
    print(f"Input prompt: {user_prompt}")
    
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

    print("\n=== LLM RESPONSE PROCESSING ===")
    try:
        # Use LLM directly for few-shot prompting
        print("Sending prompt to LLM...")
        response = llm.call([{"role": "user", "content": few_shot_prompt}])
        
        # Extract JSON array from response
        response_text = str(response)
        print(f"\nRaw LLM response:\n{response_text}")
        
        # Try to find JSON array in the response
        if '[' in response_text and ']' in response_text:
            print("\nFound JSON array in response")
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            json_str = response_text[start:end]
            print(f"Extracted JSON string: {json_str}")
            
            instructions = json.loads(json_str)
            print(f"\nParsed instructions (JSON): {instructions}")
            return instructions
        else:
            print("\nNo JSON array found, falling back to line-by-line parsing")
            # Fallback: try to parse as simple list
            lines = response_text.strip().split('\n')
            print(f"Split into {len(lines)} lines")
            
            instructions = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('[') and not line.startswith(']'):
                    # Remove quotes and clean up
                    original_line = line
                    line = line.strip('"').strip("'").strip(',')
                    if line and len(line) > 10:  # Only meaningful instructions
                        instructions.append(line)
                        print(f"Line {i}: '{original_line}' -> '{line}' (added)")
                    else:
                        print(f"Line {i}: '{original_line}' -> '{line}' (skipped - too short)")
                else:
                    print(f"Line {i}: '{line}' (skipped - bracket)")
            
            print(f"\nFinal instructions from fallback: {instructions}")
            return instructions if instructions else [user_prompt]
            
    except Exception as e:
        print(f"\nError in instruction processing: {str(e)}")
        print("Falling back to original prompt")
        return [user_prompt]

def process_single_instruction_with_retry(instruction, current_svg, gradient_parser, svg_modifier, integrity_checker, max_retries=3):
    """Process a single instruction with retry logic for rate limiting"""
    
    print("\n=== INSTRUCTION PROCESSING WITH RETRY ===")
    print(f"Processing instruction: {instruction}")
    print(f"Current SVG length: {len(current_svg)} characters")
    
    for attempt in range(max_retries):
        try:
            print(f"\nAttempt {attempt + 1}/{max_retries}")
            result = process_single_instruction(instruction, current_svg, gradient_parser, svg_modifier, integrity_checker)
            print(f"Successfully processed instruction on attempt {attempt + 1}")
            return result
        except Exception as e:
            print(f"\nError on attempt {attempt + 1}: {str(e)}")
            if "429" in str(e) or "rate" in str(e).lower():
                wait_time = (attempt + 1) * 20  # 20, 40, 60 seconds
                print(f"Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    print("Max retries reached. Skipping this instruction.")
                    return current_svg
            else:
                print(f"Non-rate-limit error: {e}")
                return current_svg
    
    return current_svg

def process_single_instruction(instruction, current_svg, gradient_parser, svg_modifier, integrity_checker):
    """Process a single instruction using the 3-agent crew"""
    
    print(f"\n=== PROCESSING SINGLE INSTRUCTION ===")
    print(f"Instruction: {instruction}")
    print(f"Current SVG length: {len(current_svg)} characters")
    
    # Task 1: Parse gradient specifications
    print("\nCreating parse task...")
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
    print("\nCreating modify task...")
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
    print("\nCreating validate task...")
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
    print("\nCreating crew with tasks...")
    crew = Crew(
        agents=[gradient_parser, svg_modifier, integrity_checker],
        tasks=[parse_task, modify_task, validate_task],
        verbose=True
    )
    
    # Execute the crew
    print("\nExecuting crew...")
    result = crew.kickoff()
    
    # Extract clean SVG from result
    print("\nProcessing crew result...")
    final_svg = str(result)
    print(f"Raw result length: {len(final_svg)} characters")
    
    if '<svg' in final_svg and '</svg>' in final_svg:
        start_idx = final_svg.find('<svg')
        end_idx = final_svg.find('</svg>') + 6
        final_svg = final_svg[start_idx:end_idx]
        print(f"Extracted SVG length: {len(final_svg)} characters")
    else:
        print("Warning: Could not find SVG tags in result")
    
    return final_svg 