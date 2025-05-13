# Contributing to ClearScan

First off, thank you for considering contributing to ClearScan! It's people like you that make ClearScan such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include details about your configuration and environment

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* A clear and descriptive title
* A detailed description of the proposed functionality
* Explain why this enhancement would be useful to most ClearScan users
* List some other tools or applications where this enhancement exists, if applicable

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the Python styleguide
* Include tests for new functionality
* Document new code based on the Documentation Styleguide

## Development Process

1. Fork the repo
2. Create a new branch from `main`
3. Make your changes
4. Run tests locally
5. Push to your fork
6. Submit a Pull Request

### Local Development Setup

```bash
# Clone your fork
git clone https://github.com/deusolutions/ClearScan.git
cd ClearScan

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure for testing
cp config.yaml.example config.yaml
# Edit config.yaml with test networks (e.g., local docker networks or VMs)

# Run tests
pytest
```

### Testing with Different Networks

When testing ClearScan, it's important to verify functionality with various network configurations:

1. Local Testing
   - Use Docker networks (e.g., 172.17.0.0/16)
   - Virtual machines (e.g., 192.168.56.0/24)
   - Local network segments

2. Network Validation
   - Test with different subnet sizes (/24, /16, etc.)
   - Verify handling of unreachable networks
   - Test with both IPv4 and IPv6 networks (if supported)

3. Performance Testing
   - Test with small networks (< 256 hosts)
   - Test with medium networks (256-1024 hosts)
   - Document performance characteristics

4. Security Considerations
   - Always use test networks you have permission to scan
   - Never test against production networks without explicit permission
   - Document any security implications found during testing

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Styleguide

* Follow PEP 8
* Use Black for code formatting
* Use type hints where possible
* Write docstrings for all public methods and functions

### Documentation Styleguide

* Use Markdown for documentation
* Reference function and variable names using backticks
* Include code examples where appropriate
* Keep line length to a maximum of 80 characters

## Additional Notes

### Issue and Pull Request Labels

* `bug`: Something isn't working
* `enhancement`: New feature or request
* `documentation`: Improvements or additions to documentation
* `good first issue`: Good for newcomers
* `help wanted`: Extra attention is needed
* `question`: Further information is requested

## Recognition

Contributors who help improve ClearScan will be recognized in our README.md file and release notes. 