# Security Vulnerability Fixes

This document outlines the security vulnerabilities that have been addressed in the SoulCoreHub repository.

## Fixed Vulnerabilities

### Python Dependencies

1. **Requests**
   - **Issue**: Session object does not verify requests after making first request with verify=False
   - **Issue**: Unintended leak of Proxy-Authorization header
   - **Fix**: Updated to requests>=2.31.0 in all requirements.txt files

2. **AWS SAM CLI**
   - **Issue**: Path Traversal allows file copy to local cache
   - **Issue**: Path Traversal allows file copy to build container
   - **Issue**: Sensitive Information Exposure Through Insecure Logging
   - **Fix**: Updated to aws-sam-cli>=1.107.0

3. **scikit-learn**
   - **Issue**: Sensitive data leakage vulnerability
   - **Fix**: Updated to scikit-learn>=1.3.2

### JavaScript Dependencies

1. **nth-check**
   - **Issue**: Inefficient Regular Expression Complexity
   - **Fix**: Updated to nth-check>=2.1.1

2. **postcss**
   - **Issue**: Line return parsing error
   - **Fix**: Updated to postcss>=8.4.31

3. **cookie**
   - **Issue**: Accepts cookie name, path, and domain with out of bounds characters
   - **Fix**: Updated to cookie>=0.7.0

4. **csurf**
   - **Issue**: Depends on vulnerable versions of cookie
   - **Fix**: Removed csurf dependency

## Remaining Issues

Some vulnerabilities may still be reported by GitHub's Dependabot due to:

1. **Transitive Dependencies**: Dependencies of dependencies that are harder to update directly
2. **Incompatible Updates**: Some updates may require major version changes that could break functionality
3. **Deep Dependencies**: Vulnerabilities in deeply nested dependencies that require coordinated updates

## Best Practices for Maintaining Security

1. **Regular Updates**: Run `npm audit fix` and `pip list --outdated` regularly
2. **Dependency Scanning**: Use GitHub's Dependabot alerts to stay informed about vulnerabilities
3. **Minimal Dependencies**: Only include necessary dependencies
4. **Version Pinning**: Pin dependencies to specific versions known to be secure
5. **Security Testing**: Implement security testing as part of the CI/CD pipeline

## How to Check for Vulnerabilities

### For npm packages:
```bash
npm audit
```

### For Python packages:
```bash
pip install safety
safety check
```

## How to Fix Vulnerabilities

### For npm packages:
```bash
npm audit fix
# For more aggressive fixes (may include breaking changes)
npm audit fix --force
```

### For Python packages:
```bash
pip install --upgrade <package-name>
```
