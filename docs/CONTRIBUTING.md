# Contributing to Coda Lite

Thank you for your interest in contributing to Coda Lite! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Issues

If you encounter a bug or have a feature request:

1. Check if the issue already exists in the [GitHub Issues](https://github.com/Aladin147/Coda_Lite/issues)
2. If not, create a new issue with a descriptive title and detailed information:
   - For bugs: steps to reproduce, expected behavior, actual behavior, and environment details
   - For features: clear description of the feature and its benefits

### Contributing Code

1. Fork the repository
2. Create a new branch for your feature or bugfix: `git checkout -b feature/your-feature-name` or `git checkout -b fix/issue-description`
3. Make your changes
4. Add or update tests as necessary
5. Ensure all tests pass
6. Update documentation if needed
7. Commit your changes with clear, descriptive commit messages
8. Push to your fork
9. Submit a pull request to the main repository

### Pull Request Process

1. Ensure your PR includes a clear description of the changes and their purpose
2. Link any relevant issues using GitHub keywords (e.g., "Fixes #123")
3. Make sure all CI checks pass
4. Be responsive to feedback and be willing to make changes if requested
5. Once approved, your PR will be merged by a maintainer

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/Aladin147/Coda_Lite.git
   cd Coda_Lite
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install development dependencies:
   ```
   pip install -r requirements-dev.txt  # To be created
   ```

## Coding Standards

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules
- Include type hints where appropriate
- Keep functions focused on a single responsibility
- Write unit tests for new functionality

## Documentation

- Update documentation for any changes to the API or functionality
- Document any new features or significant changes
- Keep the README and other documentation up to date

## Testing

- Write unit tests for new functionality
- Ensure existing tests pass with your changes
- Consider edge cases and error conditions

## License

By contributing to Coda Lite, you agree that your contributions will be licensed under the project's [Apache License 2.0](../LICENSE).

---

Thank you for contributing to Coda Lite! Your efforts help make this project better for everyone.
