from config import INPUT_SVG_FILE, OUTPUT_SVG_FILE

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