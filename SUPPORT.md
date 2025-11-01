# Support

Thank you for using the Odoo AI Agent Framework! This document provides information on how to get help and support.

## 📚 Documentation

Before seeking support, please check our documentation:

- **[README](./README.md)** - Overview and quick start guide
- **[Package Documentation](./packages/)** - Individual package documentation
- **[Samples](./samples/)** - Example code and tutorials
- **[Knowledge Base](./knowledge/)** - Patterns, playbooks, and references

## 🐛 Bug Reports

If you've found a bug, please report it:

1. **Check existing issues** - Your issue may already be reported
2. **Create a new issue** - Use our [issue tracker](https://github.com/jgtolentino/ai-agency/issues)
3. **Provide details**:
   - Description of the bug
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details (OS, Python version, package versions)
   - Error messages and stack traces

## 💡 Feature Requests

Have an idea for a new feature?

1. Check if it's already been suggested
2. Open a new issue with the "enhancement" label
3. Describe the feature and its benefits
4. Provide use cases and examples

## ❓ Questions

For questions about using the framework:

### Quick Questions

- Check the [FAQ section](./README.md#-faq) in the README
- Review the [troubleshooting guide](./README.md#-troubleshooting)
- Look through [existing discussions](https://github.com/jgtolentino/ai-agency/discussions)

### Detailed Questions

- Open a new [discussion](https://github.com/jgtolentino/ai-agency/discussions)
- Provide context and what you've tried
- Include relevant code snippets

## 🔧 Troubleshooting

### Common Issues

#### Installation Problems

```bash
# Ensure you have Python 3.10+
python --version

# Create a fresh virtual environment
python -m venv venv
source venv/bin/activate

# Install from local
pip install -e packages/odoo-core
```

#### Import Errors

```bash
# Verify package installation
pip list | grep odoo-agent

# Reinstall if needed
pip install --force-reinstall -e packages/odoo-core
```

#### Test Failures

```bash
# Run with verbose output
pytest -v

# Run specific test
pytest packages/odoo-core/tests/test_agent.py -v

# Check coverage
pytest --cov=odoo_agent_core
```

### Still Having Issues?

If you're still experiencing problems:

1. Search [existing issues](https://github.com/jgtolentino/ai-agency/issues)
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Environment details
   - Error logs

## 🤝 Contributing

Want to contribute? See our [Contributing Guide](./CONTRIBUTING.md) for:

- Development setup
- Coding standards
- Testing guidelines
- Pull request process

## 📖 Learning Resources

### Odoo Development

- [Odoo Official Documentation](https://www.odoo.com/documentation/)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [Odoo Forums](https://www.odoo.com/forum/help-1)

### AI Agents

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Agent Design Patterns](./docs/design/)

### Python

- [Python Documentation](https://docs.python.org/3/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 💬 Community

Stay connected with the community:

- **GitHub Discussions** - Ask questions and share ideas
- **Issues** - Report bugs and request features
- **Pull Requests** - Contribute code and improvements

## 📧 Contact

For sensitive issues or security concerns:

- Open a security advisory (GitHub Security tab)
- Contact the maintainers privately

## ⚡ Response Times

Please note:

- This is an open-source project maintained by volunteers
- Response times may vary
- Community members may help answer questions
- Critical security issues are prioritized

## 🌟 Help Us Help You

When asking for help:

- Be specific and clear
- Provide context
- Include error messages
- Share what you've already tried
- Be patient and respectful

## 📝 Updates

Watch the repository to stay informed about:

- New releases
- Bug fixes
- Feature additions
- Security updates

## 🙏 Thank You

Thank you for being part of the Odoo AI Agent Framework community!

Your questions, bug reports, and contributions help make this project better for everyone.

---

**Need immediate help?** Check the [README](./README.md) or open an [issue](https://github.com/jgtolentino/ai-agency/issues).
