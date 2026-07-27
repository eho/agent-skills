# Authentication and backends

Read this before signing in, requesting an OTP, or depending on remote data.

Identify whether the backend is simulator-local, Mac loopback, private LAN, hosted, or proxied. Prove reachability from the selected Simulator or through an app/network observation before driving the form. Exposing a private-LAN listener requires authority beyond localhost access.

Verify that the installed artifact or Metro bundle uses the intended public-environment fingerprint without emitting values. Check the repository-owned service smoke test when available, then confirm whether the app request reaches that service. A healthy service with no request points to interaction or served configuration, not the backend.

Reuse a synthetic authenticated fixture only while its identity, expiry, permissions, isolation, and runtime binding remain compatible.

Keep OTPs, email addresses, credentials, keys, and tokens out of logs, screenshots, ledgers, comments, and regular files. Prefer repository-owned redaction-safe helpers; otherwise request a manual authentication step.
