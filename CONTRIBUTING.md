# Contributing to EcoGridIQ

Thank you for your interest in contributing to EcoGridIQ! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker
- Google Cloud SDK
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/ecogrid-iq.git
   cd ecogrid-iq
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Set up the mock device API**
   ```bash
   cd connector
   pip install -r requirements.txt
   python mock_device_api.py
   ```

## Project Structure

```
ecogrid-iq/
├── connector/          # Fivetran custom connector
├── backend/           # Cloud Run API service
├── frontend/          # Next.js dashboard
├── infrastructure/    # Deployment configs
├── notebooks/         # Data analysis notebooks
└── demo_assets/       # Sample data and demo materials
```

## Contributing Guidelines

### Code Style

- **Python**: Follow PEP 8, use type hints, and include docstrings
- **TypeScript/JavaScript**: Use ESLint and Prettier configurations
- **SQL**: Use consistent formatting and include comments

### Commit Messages

Use conventional commit format:
```
type(scope): description

feat(api): add anomaly detection endpoint
fix(ui): resolve chart rendering issue
docs(readme): update installation instructions
```

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with appropriate tests
3. Update documentation if needed
4. Submit a pull request with a clear description

### Testing

- **Backend**: Write unit tests for new API endpoints
- **Frontend**: Test components with React Testing Library
- **Integration**: Test API integration with mock data

## Development Workflow

### Adding New Features

1. **Backend API**
   - Add new endpoints in `main.py`
   - Implement business logic in separate modules
   - Add BigQuery queries in `bigquery_client.py`
   - Update API documentation

2. **Frontend Components**
   - Create reusable components in `components/`
   - Add new pages in `pages/`
   - Update context providers as needed
   - Add proper TypeScript types

3. **Data Pipeline**
   - Add new BigQuery tables in `infrastructure/`
   - Update feature engineering SQL
   - Add new anomaly detection methods

### Database Changes

1. Update schema in `infrastructure/bigquery_schema.sql`
2. Add migration scripts if needed
3. Update feature engineering queries
4. Test with sample data

### AI/ML Features

1. Add new models in `backend/vertex_client.py`
2. Update anomaly detection in `backend/anomaly_detector.py`
3. Add new prediction endpoints
4. Update frontend to display new insights

## Code Review Process

### For Contributors

- Ensure all tests pass
- Update documentation
- Add appropriate comments
- Follow coding standards
- Test with sample data

### For Reviewers

- Check code quality and style
- Verify tests are comprehensive
- Ensure security best practices
- Validate performance implications
- Check documentation updates

## Issue Reporting

### Bug Reports

Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case and benefits
- Proposed implementation approach
- Any relevant mockups or examples

## Security

- Never commit API keys or secrets
- Use environment variables for configuration
- Follow OWASP security guidelines
- Report security issues privately

## Documentation

- Update README for significant changes
- Add inline code comments
- Update API documentation
- Include examples and use cases

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Deploy to staging/production

## Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the code of conduct

## Getting Help

- Check existing issues and discussions
- Join our community Discord
- Contact maintainers directly
- Read the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
