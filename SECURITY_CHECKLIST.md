# Security Checklist for Contributors

This checklist must be completed before every commit and pull request.

## Pre-Commit Checklist

### [ ] Environment Setup
- [ ] I am using a virtual environment (`venv` or `conda`)
- [ ] I have installed dependencies from `requirements.txt`
- [ ] I have not committed any `.env` files

### [ ] Code Quality
- [ ] I have run `pre-commit` hooks (if installed)
- [ ] Code is formatted with `black`
- [ ] Imports are sorted with `isort`
- [ ] No linting errors from `flake8`
- [ ] Tests pass locally (`pytest`)

### [ ] Security Review
- [ ] I have not added any API keys, passwords, or sensitive data
- [ ] I have not hardcoded secrets in the code
- [ ] I have used environment variables for any secrets
- [ ] I have reviewed all file changes for sensitive content
- [ ] I have run `gitleaks detect` locally (if available)

### [ ] Git Practices
- [ ] I am committing to a feature branch (not `main` directly)
- [ ] Commit messages are descriptive and follow conventional commits
- [ ] I have not force-pushed to `main`
- [ ] I have resolved any merge conflicts carefully

## Pull Request Checklist

### [ ] PR Preparation
- [ ] PR has a clear title and description
- [ ] Changes are focused on a single feature/bug fix
- [ ] I have added/updated tests for my changes
- [ ] Documentation is updated if needed

### [ ] Security in PR
- [ ] No secrets are exposed in the PR diff
- [ ] Dependencies are not introducing vulnerabilities (check Dependabot alerts)
- [ ] CI checks are passing (including security scans)
- [ ] I have requested security review if changes affect authentication or data handling

### [ ] Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests pass
- [ ] No regressions in existing functionality
- [ ] Performance impact is acceptable

## Post-Merge Checklist

### [ ] After Merge
- [ ] Monitor CI/CD pipelines for failures
- [ ] Check for any security alerts from GitHub
- [ ] Update any dependent systems if needed
- [ ] Communicate changes to the team if they affect security

## Emergency Procedures

### If You Suspect a Security Issue
1. **Stop immediately** - Do not commit or push
2. **Report** - Contact security team via SECURITY.md channels
3. **Isolate** - Work in a separate branch or local copy
4. **Document** - Note what you found and steps taken

### If Secrets Are Accidentally Committed
1. **Revoke** - Immediately revoke the exposed credentials
2. **Alert** - Notify the security team
3. **Clean** - Use `git filter-repo` to remove from history
4. **Rotate** - Generate new credentials and update everywhere

## Tools and Commands

### Local Security Checks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run security scans
gitleaks detect --source .
pip install pip-audit && pip-audit

# Format code
black .
isort .
flake8 .
```

### Git Commands for Safe Commits
```bash
# Check what you're about to commit
git diff --cached

# Add files selectively
git add -p

# Amend commit if needed (before push)
git commit --amend

# Check for secrets in recent commits
git log --oneline -10 | xargs -I {} sh -c 'git show {} | gitleaks detect --stdin'
```

## Training Resources

- [OWASP Secure Coding Practices](https://owasp.org/www-pdf-archive/OWASP_SCP_Quick_Reference_Guide_v2.pdf)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/securing-your-repository)
- [Python Security Best Practices](https://docs.python.org/3/library/secrets.html)

Remember: Security is everyone's responsibility. When in doubt, ask the security team!