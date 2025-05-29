# SVG Gradient Generator

This project uses AI agents to modify SVG files by applying gradients based on natural language instructions.

## Features

- Natural language processing of gradient instructions
- Multiple agent system for parsing, modifying, and validating SVG files
- Support for linear and radial gradients
- Intelligent instruction breakdown for complex requests
- Rate limiting handling with automatic retries

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

1. Place your input SVG file as `input.svg` in the project directory
2. Run the script:
   ```bash
   python main.py
   ```
3. Enter your gradient instruction when prompted
4. The modified SVG will be saved as `output.svg`

## Example Instructions

- "Change the red rectangle to have a vertical gradient from #ff0000 to #0000ff"
- "Make the circle green, and give the rectangle a blue-yellow gradient"
- "Add a vertical red-to-blue gradient to the red rectangle and make the circle have a radial white-to-black gradient"
- "Give all rectangles sunset gradients"

## Project Structure

- `main.py` - Main entry point
- `config.py` - Configuration and environment setup
- `svg_utils.py` - SVG file handling utilities
- `agents.py` - AI agent definitions
- `instruction_processor.py` - Instruction processing logic
- `requirements.txt` - Project dependencies

## 🎨 Overview

This project uses a multi-agent AI system built with CrewAI to automatically apply gradients to SVG elements based on natural language descriptions. Simply describe what you want, and the AI agents will parse your instructions, modify the SVG, and ensure the output is valid.

## ✨ Features

- **Natural Language Processing**: Describe gradients in plain English
- **Multi-Agent Architecture**: Three specialized AI agents work together:
  - **Gradient Parser Agent**: Extracts gradient specifications from user input
  - **SVG Modifier Agent**: Applies gradients to SVG elements
  - **Integrity Checker Agent**: Validates and ensures proper SVG syntax
- **Smart Instruction Breaking**: Automatically breaks down complex instructions into actionable steps
- **Multiple Gradient Types**: Supports linear and radial gradients
- **Flexible Directions**: Vertical, horizontal, and diagonal gradient orientations
- **Rate Limiting Handling**: Built-in retry logic for API rate limits
- **Error Recovery**: Robust error handling and fallback mechanisms

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Google API key for Gemini 2.0 Flash model

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rusticai.art
```

2. Install dependencies:
```bash
pip install crewai beautifulsoup4 python-dotenv
```

3. Set up environment variables:
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### Usage

1. **Prepare your input SVG** (optional):
   - Place your SVG file as `input.svg` in the project root
   - If no input file exists, a default red rectangle will be created

2. **Run the generator**:
```bash
python main.py
```

3. **Enter your gradient instruction** when prompted:
   - Example: "Change the red rectangle to have a vertical gradient from #ff0000 to #0000ff"
   - Example: "Add a radial gradient from white to black to the circle"
   - Example: "Make all rectangles have sunset gradients"

4. **View the result**:
   - The modified SVG will be saved as `output.svg`
   - Open in any web browser or SVG viewer to see the result

## 📝 Example Instructions

### Linear Gradients
- "Change the red rectangle to have a vertical gradient from red to blue"
- "Add a horizontal gradient from #ff0000 to #00ff00 to the square"
- "Make the circle have a diagonal gradient from white to black"

### Radial Gradients
- "Add a radial gradient from center white to edge black on the circle"
- "Give the rectangle a radial sunset gradient"

### Multiple Operations
- "Make the circle green and give the rectangle a blue-yellow gradient"
- "Add vertical red-to-blue gradients to all rectangles"

## 🏗️ Architecture

### Agent Workflow
```
User Input → Instruction Breaking → Agent Pipeline → SVG Output
                                        ↓
                              Gradient Parser Agent
                                        ↓
                               SVG Modifier Agent
                                        ↓
                              Integrity Checker Agent
```

### File Structure
```
rusticai.art/
├── main.py           # Main application logic
├── input.svg         # Input SVG file
├── output.svg        # Generated output SVG
├── .env             # Environment variables (create this)
└── README.md        # This file
```

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google API key for accessing Gemini 2.0 Flash

### File Paths
- `INPUT_SVG_FILE`: Default is "input.svg"
- `OUTPUT_SVG_FILE`: Default is "output.svg"

### LLM Settings
- Model: `gemini/gemini-2.0-flash`
- Temperature: `0.3` (for consistent, focused outputs)

## 🎯 How It Works

1. **Input Processing**: The system loads your input SVG or creates a default one
2. **Instruction Parsing**: AI breaks down complex instructions into actionable steps
3. **Agent Pipeline**: Three specialized agents process each instruction:
   - Parse gradient specifications (type, direction, colors, target)
   - Modify SVG structure (add `<defs>`, create gradients, update elements)
   - Validate output (check syntax, references, structure)
4. **Output Generation**: Final validated SVG is saved to output file

## 🛠️ Technical Details

### Dependencies
- `crewai`: Multi-agent AI framework
- `beautifulsoup4`: HTML/XML parsing
- `python-dotenv`: Environment variable management
- `json`: JSON parsing for structured data
- `re`: Regular expressions for text processing
- `time`: Rate limiting and retry logic

### Supported Gradient Types
- **Linear Gradients**: Directional color transitions
  - Vertical (top to bottom)
  - Horizontal (left to right)
  - Diagonal (corner to corner)
- **Radial Gradients**: Circular color transitions from center outward

### Error Handling
- Rate limiting with exponential backoff
- Malformed instruction fallbacks
- SVG validation and correction
- API error recovery

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is open source. Please check the license file for details.

## 🔗 Related Projects

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent AI framework
- [SVG Specification](https://www.w3.org/TR/SVG/) - Official SVG documentation

---

**Made with ❤️ by RusticAI.art** 