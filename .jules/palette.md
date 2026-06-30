## 2024-05-18 - Playwright Mocking for Tauri APIs
**Learning:** When using Playwright to visually verify frontend applications that rely on Tauri's `invoke` API, simply injecting a mock function that returns `{}` or `true` can cause runtime errors if the frontend expects a specific data type (like a string).
**Action:** When mocking Tauri in Playwright using `page.add_init_script`, ensure the mocked `invoke` function returns the correct types expected by the frontend's API client (e.g., returning `"Started"` for `start_docker_backend` if the frontend expects a string).
