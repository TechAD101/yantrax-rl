Mock data removed from runtime
=============================

This repository no longer includes any runtime mock data fallbacks.

- Backend: all mock generators and fallback behaviors removed or disabled.
- Frontend: demo placeholders and mock price generation removed.
- Tests: updated to expect explicit error responses when providers are not configured.

If you still see "mock" data in production, please verify the deployed commit and Render environment variables, then redeploy.
