# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within SoulCoreHub, please send an email to security@heloim-ai.tech. All security vulnerabilities will be promptly addressed.

Please include the following information in your report:

- Type of vulnerability
- Full path of the affected file(s)
- Location of the affected code (line number)
- Proof of concept or exploit code (if possible)
- Impact of the vulnerability

## Security Measures

SoulCoreHub implements several security measures:

1. **Dependency Scanning**: Regular scanning and updating of dependencies to address known vulnerabilities
2. **Input Validation**: Thorough validation of all user inputs
3. **Authentication**: Secure authentication using AWS Cognito
4. **Authorization**: Role-based access control for API endpoints
5. **Data Encryption**: Encryption of sensitive data at rest and in transit
6. **Rate Limiting**: Protection against brute force and DoS attacks
7. **CORS Policy**: Strict Cross-Origin Resource Sharing policy

## Recent Security Updates

- May 10, 2025: Updated cookie dependency to version 0.7.0 to address GHSA-pxg6-pf52-xh8x
- May 10, 2025: Removed csurf dependency due to security concerns
- May 10, 2025: Updated all npm dependencies to latest secure versions

## Security Best Practices for Contributors

1. Keep all dependencies updated
2. Follow the principle of least privilege
3. Validate all inputs
4. Use parameterized queries for database operations
5. Implement proper error handling
6. Use secure headers
7. Follow AWS security best practices for Lambda functions and API Gateway
