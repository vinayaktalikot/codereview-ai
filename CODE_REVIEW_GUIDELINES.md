# Our Team's Official Coding Standards

## 1. Security
- **No Hardcoded Secrets:** Never hardcode API keys, passwords, or other secrets.
- **SQL Injection:** All database queries MUST use parameterized statements. Raw SQL with f-strings or string formatting is strictly forbidden.
- **Log Sanitization:** Do not log sensitive user information.

## 2. Python Best Practices
- **Clear Variable Names:** Use descriptive variable names.
- **Error Handling:** All I/O operations must have `try...except` blocks.