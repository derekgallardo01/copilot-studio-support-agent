# Troubleshooting (sample SaaS docs)

## I can't sign in
First, confirm you're using the email address your account is registered under.
Use "Forgot password" on the sign-in page to reset; the reset link is valid for
1 hour. If your organization uses SSO, sign in through your identity provider
(Okta, Microsoft Entra ID, etc.) rather than the email/password form. If you
still can't get in, contact support and include your account email.

## File upload keeps failing
Uploads are limited to 100 MB per file on Team and 500 MB on Business. Check
your file size first. If the file is under the limit and the upload still fails,
the most common cause is a corporate firewall blocking large WebSocket
connections — try from a different network. Files of unsupported types
(`.exe`, `.bat`, archives over 50 MB) are blocked for security.

## My integration is not syncing
Open Settings → Integrations and click the integration. If it shows
"Disconnected" or "Re-authorize needed", click Reconnect and complete the OAuth
flow with the third-party service. Recent permission changes on the third
party's side can silently invalidate tokens. If reconnecting doesn't help,
remove the integration and re-add it.

## I'm seeing the wrong data after switching teams
Each team has its own workspace; data isn't shared across teams. After
switching teams (top-right menu) you'll see the workspace for the team you
selected. If you expect to see specific items and don't, confirm the team
that owns them and switch into that team.

## Performance feels slow
The most common cause is browser extensions — try a private/incognito window
to confirm. We support the latest two versions of Chrome, Edge, Safari, and
Firefox. If the slowness persists on a clean browser, please report it via
the in-app feedback widget so we can investigate.
