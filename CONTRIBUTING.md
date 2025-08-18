# Contributing to AI Course Platform

Thank you for your interest in contributing to the AI Course Platform! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs
- Use the GitHub issue tracker
- Include detailed steps to reproduce the bug
- Provide your operating system and Python version
- Include any error messages or screenshots

### Suggesting Features
- Use the GitHub issue tracker with the "enhancement" label
- Describe the feature and its benefits
- Consider implementation complexity
- Check if the feature aligns with project goals

### Code Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Submit a pull request

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/ai-course-platform.git
cd ai-course-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create sample data
python manage.py populate_sample_data

# Run development server
python manage.py runserver
```

## 📝 Code Style Guidelines

### Python Code
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Django Specific
- Follow Django best practices
- Use Django's built-in features when possible
- Write clean, readable views
- Use Django forms for data validation
- Follow Django's model conventions

### HTML/CSS/JavaScript
- Use semantic HTML
- Follow Bootstrap conventions
- Write clean, readable CSS
- Use meaningful class names
- Minimize JavaScript complexity

## 🧪 Testing

### Writing Tests
- Write tests for new features
- Ensure good test coverage
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test courses
python manage.py test accounts
python manage.py test payment_system

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📋 Pull Request Guidelines

### Before Submitting
- Ensure all tests pass
- Update documentation if needed
- Check for any linting issues
- Test your changes thoroughly
- Follow the commit message format

### Commit Message Format
```
type: brief description

Detailed description if needed

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

### Pull Request Template
- Provide a clear description
- Link related issues
- Include screenshots for UI changes
- List any breaking changes
- Mention testing performed

## 🏗️ Project Structure

### Apps
- `courses`: Course management functionality
- `accounts`: User management and authentication
- `payment_system`: Payment processing

### Key Files
- `models.py`: Database models
- `views.py`: View logic
- `urls.py`: URL routing
- `admin.py`: Admin interface
- `forms.py`: Form definitions
- `tests.py`: Test cases

## 🔧 Common Development Tasks

### Adding a New Model
1. Define the model in `models.py`
2. Create and run migrations
3. Register in `admin.py`
4. Add tests
5. Update documentation

### Creating a New View
1. Define the view in `views.py`
2. Add URL pattern in `urls.py`
3. Create template if needed
4. Add tests
5. Update documentation

### Adding a New Payment Method
1. Update `PaymentMethod.PAYMENT_CHOICES`
2. Add payment instructions
3. Update templates
4. Add admin configuration
5. Test the payment flow

## 🐛 Debugging

### Common Issues
- **Database errors**: Run `python manage.py migrate`
- **Static files**: Run `python manage.py collectstatic`
- **Import errors**: Check virtual environment activation
- **Port conflicts**: Use different port with `--port 8080`

### Debug Tools
- Django Debug Toolbar
- Python debugger (pdb)
- Browser developer tools
- Django shell: `python manage.py shell`

## 📚 Documentation

### Code Documentation
- Add docstrings to functions and classes
- Use clear, descriptive comments
- Document complex logic
- Keep README updated

### User Documentation
- Update user guides for new features
- Include screenshots for UI changes
- Provide clear installation instructions
- Document configuration options

## 🚀 Deployment

### Testing Deployment
- Test on staging environment
- Verify all features work
- Check performance
- Test payment integration
- Validate security measures

### Production Checklist
- Set `DEBUG = False`
- Configure production database
- Set up SSL/HTTPS
- Configure email settings
- Set up monitoring
- Test backup procedures

## 🤝 Community Guidelines

### Communication
- Be respectful and inclusive
- Use clear, constructive language
- Help other contributors
- Ask questions when needed
- Share knowledge and experience

### Code Review
- Provide constructive feedback
- Focus on code quality
- Suggest improvements
- Be patient with new contributors
- Explain reasoning for changes

## 📞 Getting Help

### Resources
- Django documentation
- Python documentation
- Bootstrap documentation
- GitHub discussions
- Stack Overflow

### Contact
- GitHub issues
- Email: support@aicourseplatform.com
- Discord/Slack (if available)

## 🏆 Recognition

### Contributors
- All contributors will be listed in the README
- Significant contributions will be highlighted
- Contributors will be mentioned in release notes

### Types of Contributions
- Code contributions
- Documentation improvements
- Bug reports
- Feature suggestions
- Testing and feedback
- Community support

Thank you for contributing to the AI Course Platform! Your help makes this project better for everyone.
