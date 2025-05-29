from svg_utils import load_input_svg, save_output_svg
from agents import create_3_agent_crew
from instruction_processor import break_instructions_smart, process_single_instruction_with_retry

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