# Our Team's Official Coding Standards

## 1. Security
- **No Hardcoded Secrets:** Never hardcode API keys, passwords, or other secrets directly in the code. Use environment variables or a secrets management system.
- **SQL Injection:** All database queries must use parameterized statements or an ORM. Raw SQL with f-strings or string formatting is strictly forbidden.
- **Log Sanitisation:** Do not log sensitive user information (e.g., passwords, credit card numbers, PII) in plain text.

## 2. Python Best Practices
- **Clear Variable Names:** Variable names should be descriptive (e.g., `user_profile` instead of `u_prof`). Avoid single-letter variables except in simple loops.
- **Error Handling:** All functions that perform I/O (file access, network requests) must have `try...except` blocks to gracefully handle potential errors.
- **Docstrings:** All public functions and classes must have a Google-style docstring explaining what it does, its arguments, and what it returns.

## 3. API Design
- **Consistent Naming:** API endpoints should use plural nouns for resources (e.g., `/api/users/` not `/api/user/`).
- **Standard HTTP Codes:** Use standard HTTP status codes correctly (e.g., `200` for success, `201` for creation, `400` for bad request, `404` for not found).
