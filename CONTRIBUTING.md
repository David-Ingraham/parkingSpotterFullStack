# Contributing to Parking Spotter

Thank you for your interest in contributing to Parking Spotter! This document provides guidelines for contributing to this privacy-focused parking application.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain the privacy-first mission of this project
- No harassment, discrimination, or inappropriate behavior

## Getting Started

### Prerequisites

**For Backend Development:**
- Python (3.8+)
- PostgreSQL

**For Frontend Development:**
- Node.js (v16+) - Required for React Native
- React Native development environment

**For Both:**
- Git

### Fork and Clone
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/parkingSpotter.git
   cd parkingSpotter
   ```

### Development Setup
1. **Backend Setup:**
   ```bash
   cd parkingSpotterBackend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup:**
   ```bash
   cd frontEnd
   npm install
   ```

3. **Environment Variables:**
   - Create `.env` files in both directories
   - Never commit API keys or sensitive data
   - Use example files for reference

## Development Guidelines

### Code Style

**TypeScript/JavaScript:**
- Use TypeScript for all new frontend code
- Follow ESLint configuration
- Use meaningful variable and function names
- Add type annotations for clarity

**Python:**
- Follow PEP 8 style guidelines
- Use type hints where helpful
- Keep functions focused and small
- Add docstrings for complex functions

### Privacy Requirements

**Critical: All contributions must maintain privacy principles**
- Never add user tracking or analytics
- Never store personal user data
- Process location data locally only
- No third-party data collection services
- Reject any PR that compromises privacy

### Testing

**Before submitting:**
- Test your changes locally
- Verify both Android and iOS compatibility (if frontend)
- Test API endpoints with different inputs (if backend)
- Ensure no console errors or warnings

**Automated Testing:**
- Add tests for new features
- Run existing tests before submitting
- Fix any broken tests

### Security

**Security-first development:**
- Validate all inputs
- Use parameterized queries
- Implement proper error handling
- Never expose internal system details
- Review code for potential vulnerabilities

## How to Contribute

### Bug Reports

**Before reporting:**
- Check existing issues
- Verify the bug exists in the latest version
- Test on multiple devices/platforms if possible

**When reporting include:**
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Device/OS information
- Screenshots if relevant

### Feature Requests

**Good feature requests:**
- Align with privacy-first mission
- Solve real user problems
- Are technically feasible
- Don't require user data collection

**Bad feature requests:**
- Add user accounts or tracking
- Require personal data storage
- Violate privacy principles
- Add unnecessary complexity

### Pull Requests

**Before submitting:**
1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following style guidelines

3. Test thoroughly

4. Commit with clear messages:
   ```bash
   git commit -m "Add feature: brief description"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

**PR Requirements:**
- Clear title and description
- Reference related issues
- Include testing information
- Update documentation if needed
- Maintain privacy principles

### Code Review Process

**What reviewers check:**
- Code quality and style
- Privacy compliance
- Security considerations
- Testing coverage
- Documentation updates
- Backward compatibility

**Response expectations:**
- Initial review within 48-72 hours
- Be patient with feedback rounds
- Address all reviewer comments
- Ask questions if feedback is unclear

## Project Structure

### Backend (`parkingSpotterBackend/`)
- `main.py` - Application entry point
- `routes/` - API endpoints
- `database/` - Models and configuration
- `helpers/` - Utility functions
- `scripts/` - Database and maintenance scripts

### Frontend (`frontEnd/`)
- `App.tsx` - Main application component
- `screens/` - App screens
- `components/` - Reusable UI components
- `hooks/` - Custom React hooks
- `types/` - TypeScript definitions

## Documentation

**Update documentation when:**
- Adding new features
- Changing API endpoints
- Modifying environment variables
- Changing deployment procedures

**Documentation files:**
- `README.md` - Main project documentation
- `PRIVACY.md` - Privacy policy
- `API.md` - API documentation
- `DEPLOYMENT.md` - Deployment guide

## Release Process

**For maintainers:**
1. Version bump in relevant files
2. Update CHANGELOG.md
3. Create release notes
4. Tag release in Git
5. Deploy to production
6. Update app stores if needed

## Questions?

- Check existing documentation first
- Search closed issues for similar questions
- Create a new issue with the "question" label
- Be specific about what you need help with

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Remember: Every contribution should make Parking Spotter better while maintaining our commitment to user privacy.** 