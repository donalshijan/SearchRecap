# InferenceManager

A Python toolkit for processing large datasets through AI inference, with a focus on batch processing and data filtering using OpenAI's language models.

## 🎯 Project Overview

This project addresses common inference challenges when working with large datasets and AI models:

- **Batch Processing**: Process large datasets in manageable chunks to avoid API limits
- **Data Filtering**: Use AI to intelligently filter and categorize data
- **Generic Data Processing**: Works with any type of structured JSON data (not limited to specific formats)
- **Extensible Architecture**: Framework for building custom inference pipelines with a central control panel

### 🗂️ **Input Format: JSON Files Only**

This project specifically works with **structured JSON files** as input. The system expects:

- **JSON files** containing either:
  - A direct list of data items: `["item1", "item2", "item3"]`
  - A dictionary with data under a key that matches your configured `DATA_LABEL`

- **Text files** (`.txt`) for AI prompts and instructions

### 📝 **Current Use Case: Search Query Filtering**

The initial implementation is configured to filter Google search queries to extract only those related to:
- Word definitions and meanings
- Academic/scholarly terms
- Scientific and mathematical concepts
- Idiomatic expressions
- Linguistic inquiries

**However, this is just one example configuration.** The system is designed to work with any type of data by simply updating the configuration.

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd InferenceManager
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   MODEL_NAME=gpt-model-of-choice
   ```

## 🚀 Quick Start

### 1. Prepare Your Data

Your input JSON file should have one of these structures:

**Option A: Direct list**
```json
[
  "what is machine learning",
  "definition of algorithm",
  "meaning of serendipity"
]
```

**Option B: Dictionary with matching key**
```json
{
  "queries": [
    "what is machine learning",
    "definition of algorithm",
    "meaning of serendipity"
  ]
}
```

**Important**: The key name in your JSON must match the `DATA_LABEL` you configure in `config.py`.

### 2. Configure Your Use Case

Edit `config.py` to match your data and task:

```python
# Data label configuration
DATA_LABEL: str = "queries"  # What you're processing
DATA_DESCRIPTION: str = "Google search queries"  # Human-readable description

# Task configuration  
TASK_DESCRIPTION: str = "filter for educational content"
TASK_INSTRUCTIONS: str = "Extract only educational and learning-related items"
```

### 3. Run the Inference

```bash
# Using the main control panel (recommended)
python main.py

# Or use the specific batch processing script directly
python runInferenceInBatches.py
```

### 4. Check Results

The filtered results will be saved to your configured output file.

## ⚙️ Configuration

Edit `config.py` to customize:

- **Input/Output files**: Change file paths
- **Batch size**: Adjust for your API limits (default: 200)
- **Model**: Choose OpenAI model (default: gpt-4o-mini)
- **Inference method**: Choose which inference strategy to use
- **Data label**: Specify the key name in your JSON file
- **Task description**: Define what you want to accomplish

## 🔧 Customization Examples

### Example 1: Company Name Filtering
```python
DATA_LABEL: str = "companies"
DATA_DESCRIPTION: str = "company names from a business directory"
TASK_DESCRIPTION: str = "filter for technology companies"
TASK_INSTRUCTIONS: str = "Extract only company names that are clearly technology or software companies"
```

**Required JSON structure:**
```json
{
  "companies": ["Apple Inc", "Microsoft", "Local Bakery", "Google LLC"]
}
```

### Example 2: Product Classification
```python
DATA_LABEL: str = "products"
DATA_DESCRIPTION: str = "product names from an e-commerce catalog"
TASK_DESCRIPTION: str = "categorize by product type"
TASK_INSTRUCTIONS: str = "Classify each product as electronics, clothing, books, or other"
```

**Required JSON structure:**
```json
{
  "products": ["iPhone 15", "Nike Shoes", "Python Book", "Coffee Maker"]
}
```

### Example 3: Name Analysis
```python
DATA_LABEL: str = "names"
DATA_DESCRIPTION: str = "list of people's names"
TASK_DESCRIPTION: str = "identify gender-neutral names"
TASK_INSTRUCTIONS: str = "Extract names that could be used for either gender"
```

**Required JSON structure:**
```json
{
  "names": ["Alex", "Jordan", "Taylor", "Casey"]
}
```

## 🛠️ Development Tools

### Type Checking with mypy
```bash
mypy . --show-error-codes
```

### Linting with ruff
```bash
ruff check .
ruff check . --fix  # Auto-fix issues
```

### Code Formatting
```bash
ruff format .
```

## 🚧 Future Enhancements

- [ ] Support for multiple AI providers (Claude, Gemini, etc.)
- [ ] Progress bars and better logging
- [ ] Retry mechanisms for failed API calls
- [ ] Parallel processing capabilities
- [ ] Web interface for easy data upload
- [ ] Pre-built inference templates for common tasks
- [ ] Support for other file formats (CSV, Excel, etc.)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `mypy . && ruff check .`
5. Submit a pull request

## 📄 License

The project contained in the folder of this READM.md file is licensed under the [Apache License 2.0](./LICENSE).

You are free to use, modify, and self-host this software, provided that you include the original copyright and license notice.

---

**Note**: This project requires an OpenAI API key. Make sure to keep your API key secure and never commit it to version control.

**Important**: This project is designed to work specifically with JSON files. If you need to process other file formats, you'll need to convert them to JSON first or extend the system to handle additional formats.

**Key Requirement**: The key name in your JSON file must exactly match the `DATA_LABEL` you configure in `config.py`. This ensures consistency and prevents errors.

