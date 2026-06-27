# Product Features (sample SaaS docs)

## Plans
We offer three subscription plans: Starter, Team, and Business. Starter is free
for up to 3 users with 1 GB of storage. Team is $12 per user per month and
includes 50 GB of storage, integrations, and priority email support. Business
is $24 per user per month and adds SSO, audit logging, an admin console, and a
99.9% uptime SLA. Annual billing receives a 17% discount on all paid plans.

## Integrations
The Team and Business plans include integrations with Slack, Microsoft Teams,
Google Drive, GitHub, and Jira. Connect them from Settings → Integrations.
Each integration uses OAuth — we never store passwords.

## Single Sign-On (SSO)
SSO is available on the Business plan. We support SAML 2.0 and OIDC. To
configure SSO, an administrator opens the Admin Console, chooses the identity
provider (Okta, Microsoft Entra ID, Google Workspace, or a generic SAML
provider), and pastes the metadata URL. Existing users are matched by email.

## Mobile apps
Native iOS and Android apps are available. The mobile apps support offline mode
and push notifications. Sign in with the same account you use on the web.
