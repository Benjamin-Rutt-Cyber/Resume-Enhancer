---
name: rest-api-design
description: Expert knowledge in REST API design principles including resource naming, HTTP methods, status codes, pagination, versioning, and API best practices.
allowed-tools: [Read, Write, Edit, Bash]
---

# REST API Design Skill

Comprehensive knowledge for designing well-structured, intuitive RESTful APIs.

## Quick Start

### Basic REST Principles

**REST (Representational State Transfer)** is an architectural style for designing networked applications.

**Key Principles:**
1. **Client-Server** - Separation of concerns
2. **Stateless** - Each request contains all necessary information
3. **Cacheable** - Responses must define themselves as cacheable or not
4. **Uniform Interface** - Consistent resource identification and manipulation
5. **Layered System** - Client doesn't know if connected to end server or intermediary

### Resource-Based URLs

```
✅ GOOD (Resource-oriented):
GET    /users              # Get all users
GET    /users/123          # Get specific user
POST   /users              # Create new user
PUT    /users/123          # Update user (full)
PATCH  /users/123          # Update user (partial)
DELETE /users/123          # Delete user

❌ BAD (Action-oriented):
GET    /getUsers
POST   /createUser
POST   /updateUser
POST   /deleteUser/123
```

---

## HTTP Methods

### GET - Retrieve Resources

```http
# Get collection
GET /api/users
Response: 200 OK
[
  { "id": 1, "name": "Alice" },
  { "id": 2, "name": "Bob" }
]

# Get single resource
GET /api/users/1
Response: 200 OK
{ "id": 1, "name": "Alice", "email": "alice@example.com" }

# Resource not found
GET /api/users/999
Response: 404 Not Found
{ "error": "User not found" }
```

**Characteristics:**
- Safe (no side effects)
- Idempotent (same result every time)
- Cacheable

### POST - Create Resources

```http
# Create new resource
POST /api/users
Content-Type: application/json

{
  "name": "Charlie",
  "email": "charlie@example.com"
}

Response: 201 Created
Location: /api/users/3
{
  "id": 3,
  "name": "Charlie",
  "email": "charlie@example.com",
  "created_at": "2023-01-15T10:30:00Z"
}

# Validation error
POST /api/users
{ "name": "" }

Response: 400 Bad Request
{
  "error": "Validation failed",
  "details": {
    "name": "Name is required",
    "email": "Email is required"
  }
}
```

**Characteristics:**
- Not safe (creates resource)
- Not idempotent (multiple calls create multiple resources)
- Returns 201 Created with Location header

### PUT - Full Update

```http
# Replace entire resource
PUT /api/users/1
Content-Type: application/json

{
  "name": "Alice Updated",
  "email": "alice.new@example.com"
}

Response: 200 OK
{
  "id": 1,
  "name": "Alice Updated",
  "email": "alice.new@example.com",
  "updated_at": "2023-01-15T11:00:00Z"
}
```

**Characteristics:**
- Not safe (modifies resource)
- Idempotent (same result every time)
- Requires full resource representation

### PATCH - Partial Update

```http
# Update specific fields
PATCH /api/users/1
Content-Type: application/json

{
  "name": "Alice Modified"
}

Response: 200 OK
{
  "id": 1,
  "name": "Alice Modified",
  "email": "alice@example.com",  # Unchanged
  "updated_at": "2023-01-15T11:30:00Z"
}
```

**Characteristics:**
- Not safe (modifies resource)
- May or may not be idempotent
- Only sends changed fields

### DELETE - Remove Resources

```http
# Delete resource
DELETE /api/users/1

Response: 204 No Content

# Or with confirmation
Response: 200 OK
{
  "message": "User deleted successfully"
}

# Resource already deleted
DELETE /api/users/1

Response: 404 Not Found
```

**Characteristics:**
- Not safe (removes resource)
- Idempotent (multiple deletes have same effect)
- Returns 204 No Content or 200 OK

---

## HTTP Status Codes

### Success (2xx)

```
200 OK              - Request succeeded
201 Created         - Resource created (POST)
202 Accepted        - Request accepted, processing async
204 No Content      - Success, no response body (DELETE)
```

### Redirection (3xx)

```
301 Moved Permanently   - Resource permanently moved
302 Found               - Temporary redirect
304 Not Modified        - Cached version still valid
```

### Client Errors (4xx)

```
400 Bad Request         - Invalid request format/validation
401 Unauthorized        - Authentication required
403 Forbidden           - Authenticated but not authorized
404 Not Found           - Resource doesn't exist
405 Method Not Allowed  - HTTP method not supported
409 Conflict            - Resource conflict (duplicate email)
422 Unprocessable       - Validation error
429 Too Many Requests   - Rate limit exceeded
```

### Server Errors (5xx)

```
500 Internal Server Error   - Generic server error
502 Bad Gateway             - Invalid response from upstream
503 Service Unavailable     - Server temporarily unavailable
504 Gateway Timeout         - Upstream server timeout
```

---

## Resource Naming

### Best Practices

```
✅ GOOD:
/users                  # Plural nouns
/users/123/posts        # Nested resources
/products/456/reviews   # Related resources
/posts?status=published # Query parameters for filtering

❌ BAD:
/user                   # Singular
/getUser
/createPost
/posts/create           # Action in URL
```

### Hierarchical Resources

```http
# User's posts
GET /users/123/posts

# Specific user's post
GET /users/123/posts/456

# Post's comments
GET /posts/456/comments

# Alternative for independent access
GET /posts/456          # Access post directly
GET /comments?post_id=456  # Filter comments by post
```

### URL Structure Rules

1. **Use nouns, not verbs** - Resources are nouns, HTTP methods are verbs
2. **Plural names** - `/users` not `/user`
3. **Lowercase** - `/users` not `/Users`
4. **Hyphens for readability** - `/user-profiles` not `/user_profiles`
5. **No trailing slashes** - `/users` not `/users/`
6. **Version in URL** - `/v1/users` or `/api/v1/users`

---

## Pagination

### Offset-Based (Simple)

```http
GET /api/posts?limit=20&offset=40

Response:
{
  "data": [ /* 20 posts */ ],
  "pagination": {
    "limit": 20,
    "offset": 40,
    "total": 150,
    "has_more": true
  }
}
```

**Pros:** Simple, can jump to any page
**Cons:** Performance degrades with large offsets, inconsistent results if data changes

### Cursor-Based (Performance)

```http
GET /api/posts?limit=20&cursor=eyJpZCI6MTIzfQ

Response:
{
  "data": [ /* 20 posts */ ],
  "pagination": {
    "next_cursor": "eyJpZCI6MTQzfQ",
    "has_more": true
  }
}

# Next request
GET /api/posts?limit=20&cursor=eyJpZCI6MTQzfQ
```

**Pros:** Consistent results, better performance
**Cons:** Can't jump to specific page, more complex

### Page-Based (User-Friendly)

```http
GET /api/posts?page=3&per_page=20

Response:
{
  "data": [ /* 20 posts */ ],
  "pagination": {
    "current_page": 3,
    "per_page": 20,
    "total_pages": 8,
    "total_items": 150
  }
}
```

---

## Filtering, Sorting, Searching

### Filtering

```http
# Single filter
GET /api/products?category=electronics

# Multiple filters
GET /api/products?category=electronics&price_min=100&price_max=500

# Boolean filters
GET /api/users?is_active=true

# Date filters
GET /api/orders?created_after=2023-01-01&created_before=2023-12-31
```

### Sorting

```http
# Single field ascending
GET /api/products?sort=price

# Single field descending
GET /api/products?sort=-price

# Multiple fields
GET /api/products?sort=category,-price,name

# Alternative syntax
GET /api/products?sort_by=price&order=desc
```

### Searching

```http
# Full-text search
GET /api/products?q=wireless+headphones

# Field-specific search
GET /api/users?email_contains=@example.com

# Advanced search
GET /api/products?search[name]=phone&search[description]=samsung
```

### Field Selection

```http
# Select specific fields
GET /api/users?fields=id,name,email

# Exclude fields
GET /api/users?exclude=password_hash,internal_notes
```

---

## Versioning

### URL Versioning (Most Common)

```http
GET /v1/users
GET /v2/users

# With api prefix
GET /api/v1/users
GET /api/v2/users
```

**Pros:** Simple, clear, easy to route
**Cons:** Multiple URLs for same resource

### Header Versioning

```http
GET /users
Accept: application/vnd.myapp.v1+json

GET /users
Accept: application/vnd.myapp.v2+json
```

**Pros:** Single URL, cleaner
**Cons:** Less visible, harder to test

### Query Parameter

```http
GET /users?version=1
GET /users?api-version=2
```

**Pros:** Simple
**Cons:** Not RESTful, can interfere with caching

### Content Negotiation (Custom Media Types)

```http
GET /users
Accept: application/vnd.myapp.user.v1+json
```

**Pros:** Most RESTful
**Cons:** Complex, less common

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters"
      }
    ],
    "request_id": "req_abc123",
    "timestamp": "2023-01-15T10:30:00Z"
  }
}
```

### Error Code Examples

```http
# Validation error
400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data"
  }
}

# Authentication error
401 Unauthorized
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}

# Authorization error
403 Forbidden
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to access this resource"
  }
}

# Not found
404 Not Found
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}

# Rate limit
429 Too Many Requests
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retry_after": 60
  }
}
```

---

## HATEOAS (Hypermedia)

```json
GET /api/users/1

{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "_links": {
    "self": { "href": "/api/users/1" },
    "posts": { "href": "/api/users/1/posts" },
    "update": { "href": "/api/users/1", "method": "PUT" },
    "delete": { "href": "/api/users/1", "method": "DELETE" }
  }
}
```

**Benefits:**
- Self-documenting
- Client discovers available actions
- Server can change URLs without breaking clients

---

## Best Practices

### 1. Use JSON

```http
Content-Type: application/json

{
  "name": "value",
  "nested": {
    "field": "value"
  }
}
```

### 2. Consistent Naming

```json
// ✅ GOOD: snake_case
{
  "first_name": "Alice",
  "created_at": "2023-01-15"
}

// Or camelCase (pick one and be consistent)
{
  "firstName": "Alice",
  "createdAt": "2023-01-15"
}
```

### 3. ISO 8601 Dates

```json
{
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": "2023-01-15T11:00:00+00:00"
}
```

### 4. Envelope Responses (Optional)

```json
{
  "data": { /* actual resource */ },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2023-01-15T10:30:00Z"
  }
}
```

### 5. Rate Limiting Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1673780000
```

### 6. Bulk Operations

```http
# Bulk create
POST /api/users/bulk
[
  { "name": "Alice", "email": "alice@example.com" },
  { "name": "Bob", "email": "bob@example.com" }
]

Response: 207 Multi-Status
{
  "results": [
    { "status": 201, "data": { "id": 1, "name": "Alice" } },
    { "status": 400, "error": "Email already exists" }
  ]
}

# Bulk update
PATCH /api/users/bulk
{
  "ids": [1, 2, 3],
  "update": { "status": "active" }
}

# Bulk delete
DELETE /api/users?ids=1,2,3
```

### 7. Idempotency Keys

```http
POST /api/orders
Idempotency-Key: unique-key-123

# Retry with same key returns same response
POST /api/orders
Idempotency-Key: unique-key-123

Response: 200 OK (same order, not created again)
```

---

## Common Patterns

### Nested Resources vs Query Parameters

```http
# Nested (when resource belongs to parent)
GET /users/1/posts
POST /users/1/posts

# Query parameter (when resource is independent)
GET /posts?user_id=1
POST /posts { "user_id": 1, ... }
```

### Soft Delete

```http
# Option 1: Update status
PATCH /api/users/1
{ "status": "deleted" }

# Option 2: Dedicated endpoint
DELETE /api/users/1 (soft delete)
DELETE /api/users/1?permanent=true (hard delete)

# Option 3: Archive endpoint
POST /api/users/1/archive
```

### File Uploads

```http
POST /api/users/1/avatar
Content-Type: multipart/form-data

file: [binary data]

Response: 201 Created
{
  "url": "https://cdn.example.com/avatars/user1.jpg",
  "size": 52468,
  "mime_type": "image/jpeg"
}
```

### Webhooks Configuration

```http
# Register webhook
POST /api/webhooks
{
  "url": "https://myapp.com/webhooks",
  "events": ["user.created", "user.updated"],
  "secret": "webhook_secret"
}

# List webhooks
GET /api/webhooks

# Delete webhook
DELETE /api/webhooks/123
```

---

## Documentation

### OpenAPI/Swagger Example

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0

paths:
  /users:
    get:
      summary: Get all users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
          format: email
```

---

## API Design Checklist

- [ ] Use nouns for resources, not verbs
- [ ] Use plural resource names
- [ ] Use HTTP methods correctly
- [ ] Return appropriate status codes
- [ ] Implement pagination for collections
- [ ] Support filtering, sorting, searching
- [ ] Version your API
- [ ] Provide consistent error responses
- [ ] Use JSON as default format
- [ ] Use ISO 8601 for dates
- [ ] Implement rate limiting
- [ ] Support field selection
- [ ] Document with OpenAPI/Swagger
- [ ] Use HTTPS
- [ ] Implement proper authentication
- [ ] Make it backward compatible
- [ ] Add request/response examples

---

## Resources

- REST API Tutorial: https://restfulapi.net/
- HTTP Status Codes: https://httpstatuses.com/
- OpenAPI Specification: https://swagger.io/specification/
- JSON:API Specification: https://jsonapi.org/
- RESTful API Guidelines: https://github.com/microsoft/api-guidelines
