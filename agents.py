from crewai import Agent, LLM
from config import api_key

def create_llm():
    """Initialize and return LLM instance"""
    return LLM(
        model="gemini/gemini-2.0-flash",
        temperature=0.3,
        api_key=api_key
    )

def create_3_agent_crew():
    """Create the 3-agent crew that will be reused"""
    llm = create_llm()
    
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