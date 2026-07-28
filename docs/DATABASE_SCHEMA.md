# Database Schema

```mermaid
erDiagram
  USERS ||--o{ URLS : owns
  USERS ||--o{ REFRESH_TOKENS : has
  URLS ||--o{ CLICKS : records

  USERS {
    int id PK
    string email UK
    string username UK
    string hashed_password
    string full_name
    bool is_active
    bool is_admin
    datetime created_at
    datetime updated_at
  }

  URLS {
    int id PK
    text original_url
    string short_code UK
    string custom_alias UK
    string title
    text description
    string password_hash
    bool is_one_time
    datetime used_at
    datetime expires_at
    bool is_active
    int user_id FK
    datetime created_at
    datetime updated_at
  }

  CLICKS {
    int id PK
    int url_id FK
    string ip_address
    string user_agent
    string referrer
    string country
    string browser
    string device
    datetime created_at
  }

  REFRESH_TOKENS {
    int id PK
    string token_hash UK
    int user_id FK
    datetime expires_at
    datetime revoked_at
    datetime created_at
  }
```

## Indexes

- `users.email`
- `users.username`
- `urls.short_code`
- `urls.custom_alias`
- `urls.user_id, urls.created_at`
- `urls.user_id, urls.is_active`
- `clicks.url_id, clicks.created_at`
- `refresh_tokens.token_hash`
