# Security Implementation Guide

## JWT Authentication

### Overview
The system uses JWT (JSON Web Tokens) for authentication with a two-token system:
- Access Token: Short-lived token for API access
- Refresh Token: Long-lived token for obtaining new access tokens

### Configuration
Required environment variables (see config/env.template):
- JWT_SECRET: Secret key for token signing (min 32 characters)
- JWT_ALGORITHM: Token signing algorithm (default: HS256)
- JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Access token lifetime
- JWT_REFRESH_TOKEN_EXPIRE_DAYS: Refresh token lifetime

### Frontend Implementation
The frontend security system (static/js/systems/security.js) provides:
- Token management (storage, refresh, cleanup)
- Authenticated fetch wrapper
- Login/logout handling

### Backend Implementation
The backend JWT implementation includes:
- Token generation and validation
- Refresh token rotation
- Role-based access control middleware

### API Endpoints
- POST /api/auth/login: Obtain tokens
- POST /api/auth/refresh: Refresh access token
- POST /api/auth/logout: Invalidate tokens
- POST /api/auth/validate: Validate token

### Security Considerations
1. Token Storage:
   - Access token: localStorage (short-lived)
   - Refresh token: httpOnly cookie (recommended)

2. Token Refresh:
   - Automatic refresh on 401 responses
   - Token rotation on refresh

3. CSRF Protection:
   - Required for cookie-based refresh tokens
   - Use double-submit pattern

4. XSS Protection:
   - Content Security Policy (CSP)
   - Input sanitization

### Implementation Status
- [x] Frontend token management
- [x] Token refresh logic
- [x] Authentication middleware
- [ ] Role-based access control
- [ ] Session management
- [ ] Refresh token rotation