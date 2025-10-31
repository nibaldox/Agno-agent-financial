# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 3.x.x   | :white_check_mark: |
| 2.x.x   | :x:                |
| < 2.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it to us as follows:

### Contact Information
- **Email**: security@yourdomain.com (replace with actual contact)
- **GitHub Security Advisories**: [Create a private advisory](https://github.com/nibaldox/Agno-agent-financial/security/advisories/new)
- **Response Time**: We aim to respond within 48 hours

### What to Include
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes

### Our Process
1. Acknowledge receipt within 48 hours
2. Investigate and validate the report
3. Develop and test a fix
4. Publish a security advisory
5. Release a patch

## Security Best Practices

### For Contributors
- Never commit API keys, passwords, or sensitive data
- Use environment variables for secrets
- Run `pre-commit` hooks before committing
- Review changes for sensitive data before pushing

### For Users
- Keep API keys secure and rotate them regularly
- Use virtual environments for Python dependencies
- Monitor your GitHub repository for security alerts
- Keep dependencies updated

## Key Rotation Policy

### API Keys
- Rotate OpenRouter and DeepSeek keys every 90 days
- Immediately rotate any key that may have been exposed
- Use GitHub Secrets for CI/CD pipelines

### GitHub Tokens
- Use fine-grained personal access tokens
- Rotate tokens every 30 days
- Limit token scopes to minimum required permissions

## Incident Response Playbook

### If Secrets Are Exposed
1. **Immediate Actions**:
   - Revoke the exposed credentials
   - Generate new keys/tokens
   - Notify affected parties

2. **Repository Cleanup**:
   ```bash
   # Install git-filter-repo
   pip install git-filter-repo

   # Remove sensitive files from history
   git filter-repo --invert-paths --paths sensitive_file.txt

   # Force push (coordinate with team)
   git push --force --all
   ```

3. **Communication**:
   - Alert all contributors to re-clone the repository
   - Update documentation
   - Monitor for unauthorized access

### If Repository Is Compromised
1. Transfer ownership to a new repository
2. Audit all recent commits
3. Revoke all associated credentials
4. Notify GitHub support if needed

## Security Tools

We use the following tools for security:

- **gitleaks**: Secret detection in code and history
- **pip-audit**: Python dependency vulnerability scanning
- **pre-commit hooks**: Code quality and secret prevention
- **GitHub Security Advisories**: Vulnerability management
- **Dependabot**: Automated dependency updates

## Compliance

This project aims to follow:
- OWASP guidelines for secure coding
- GitHub's security best practices
- Responsible disclosure principles

## Disclaimer

This software is provided "as is" without warranty. Users are responsible for securing their own deployments and API keys.