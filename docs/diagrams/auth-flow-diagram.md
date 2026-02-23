# Authentication Flow Diagram

This diagram shows the complete authentication flow in the Auto Bidder platform.

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AuthService
    participant Database
    
    Note over User,Database: User Signup
    User->>Frontend: Enter email & password
    Frontend->>API: POST /auth/signup
    API->>AuthService: create_user()
    AuthService->>AuthService: Hash password (bcrypt)
    AuthService->>Database: INSERT INTO users
    Database-->>AuthService: User created
    AuthService-->>API: User object
    API-->>Frontend: 201 Created
    Frontend-->>User: Account created
    
    Note over User,Database: User Login
    User->>Frontend: Enter credentials
    Frontend->>API: POST /auth/login
    API->>AuthService: authenticate()
    AuthService->>Database: SELECT user
    Database-->>AuthService: User data
    AuthService->>AuthService: Verify password
    AuthService->>AuthService: Generate JWT token
    AuthService-->>API: JWT token + user info
    API-->>Frontend: 200 OK with token
    Frontend->>Frontend: Store token in memory/storage
    Frontend-->>User: Redirect to dashboard
    
    Note over User,Database: Authenticated Request
    User->>Frontend: Access protected resource
    Frontend->>API: GET /api/resource (Authorization: Bearer <token>)
    API->>AuthService: verify_token()
    AuthService->>AuthService: Decode JWT & validate
    AuthService-->>API: User ID
    API->>Database: Fetch user data
    Database-->>API: User data
    API-->>Frontend: 200 OK with data
    Frontend-->>User: Display resource
    
    Note over User,Database: Token Expiration
    User->>Frontend: Request with expired token
    Frontend->>API: GET /api/resource (expired token)
    API->>AuthService: verify_token()
    AuthService-->>API: 401 Unauthorized
    API-->>Frontend: 401 Token expired
    Frontend->>Frontend: Clear stored token
    Frontend-->>User: Redirect to login
```

## Key Security Features

1. **Password Hashing**: bcrypt with automatic salt generation
2. **JWT Tokens**: Stateless authentication with configurable expiration
3. **Token Validation**: Every protected endpoint validates JWT signature
4. **Secure Storage**: Passwords truncated to 72 bytes for bcrypt compatibility
5. **Error Handling**: Generic error messages to prevent user enumeration

## Token Structure

```json
{
  "sub": "user_id",
  "exp": 1234567890,
  "iat": 1234567000
}
```

## Environment Configuration

- `JWT_SECRET`: Cryptographically secure 64-byte secret
- `JWT_ALGORITHM`: HS256 (HMAC with SHA-256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token lifetime (default: 30 days)
