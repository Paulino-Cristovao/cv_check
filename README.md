# CV Check - AI-Powered Resume Optimizer for PhD Holders

🎯 **AI-powered resume analysis and optimization specifically designed for PhD holders in the French job market**

## Overview

CV Check is a specialized tool that helps PhD holders optimize their resumes for better selection rates in the French job market. The system analyzes resumes against specific job descriptions and provides targeted recommendations to address overqualification bias and improve compatibility scores.

## Features

### 🔍 **Resume Analysis**
- **Compatibility Score**: 0-100 matching score with detailed breakdown
- **Strong Points**: Identification of strengths with leverage strategies
- **Weak Points**: Areas for improvement with impact assessment
- **Smart Recommendations**: Specific, actionable improvements with priority ranking

### 📋 **Interview Preparation**
- **Personalized Questions**: Predicted interview questions based on job requirements
- **Answer Frameworks**: STAR method templates and suggested responses
- **Company Research**: Role and industry analysis
- **Overqualification Handling**: Strategies for PhD candidates
- **Downloadable Guide**: Professional Word document with comprehensive preparation materials

### 🇫🇷 **French Market Specialization**
- PhD overqualification risk assessment
- French hiring culture considerations
- European CV standards compliance
- Industry-specific recommendations

## Installation

### Prerequisites
- Python 3.9 or higher
- OpenAI API key
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cv_check
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

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Usage

### Running the Application

1. **Start the application**
   ```bash
   python run_app.py
   ```

2. **Access the web interface**
   - Open your browser to `http://localhost:7860`
   - Upload your resume (PDF or DOCX format)
   - Paste the job description
   - Click "Analyze Resume"

### Input Requirements

- **Resume**: PDF or DOCX format, complete and up-to-date
- **Job Description**: Full text including requirements, responsibilities, and company information

### Output

1. **Compatibility Score**: Percentage match with color-coded indicator
2. **Strong Points**: Your advantages with tips on how to leverage them
3. **Weak Points**: Areas needing improvement with impact explanations
4. **Recommendations**: Prioritized action items with implementation guidance
5. **Interview Preparation**: Downloadable Word document with comprehensive prep materials

## Development

### Project Structure

```
cv_check/
├── src/                          # Source code
│   ├── parsers/                  # Document parsing (PDF, DOCX)
│   ├── analyzer/                 # Resume and job analysis
│   ├── generator/                # Document and recommendation generation
│   ├── utils/                    # Utilities and OpenAI client
│   └── app.py                    # Main Gradio application
├── tests/                        # Test suite
├── templates/                    # Document templates
├── outputs/                      # Generated documents
└── requirements.txt              # Dependencies
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_parsers.py
```

### Code Quality

```bash
# Type checking
mypy src/

# Code linting
pylint src/

# Code formatting
black src/ tests/
```

## API Integration

### OpenAI Configuration

The application uses OpenAI GPT-4 for:
- Resume and job description analysis
- Gap analysis and recommendations
- Interview preparation content generation

Ensure your API key has sufficient credits and access to GPT-4.

### Cost Considerations

- Typical analysis costs: $0.10-0.30 per resume-job pair
- Interview prep generation: $0.20-0.50 per document
- Implement usage tracking for production deployments

## Deployment

### Local Development
```bash
python run_app.py
```

### Production Deployment

1. **Environment Setup**
   ```bash
   export OPENAI_API_KEY="your-production-key"
   export ENVIRONMENT="production"
   ```

2. **Docker Deployment** (Optional)
   ```bash
   docker build -t cv-check .
   docker run -p 7860:7860 -e OPENAI_API_KEY="your-key" cv-check
   ```

## Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure all tests pass and code quality checks succeed
5. Submit a pull request

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive tests (target >80% coverage)
- Include docstrings for all public functions
- Use meaningful variable and function names

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Verify API key is set correctly
   - Check API key has sufficient credits
   - Ensure access to GPT-4 model

2. **File Parsing Issues**
   - Supported formats: PDF, DOCX, DOC
   - Ensure files are not password protected
   - Check file size is reasonable (<10MB)

3. **Analysis Failures**
   - Verify resume and job description are in text format
   - Check for special characters or encoding issues
   - Ensure job description is comprehensive

### Logging

Application logs are written to:
- Console output (INFO level)
- `cv_check.log` file (DEBUG level)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review existing GitHub issues
- Create a new issue with detailed information

## Acknowledgments

- OpenAI for GPT-4 API
- Gradio for the web interface framework
- Contributors and testers

---

**Built specifically for PhD holders navigating the French job market** 🇫🇷

*Helping bridge the gap between academic excellence and industry opportunity*