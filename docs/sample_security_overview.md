# Acme Cloud Storage — Security Overview

## Encryption
All files are encrypted in transit using TLS 1.2 or higher between your
device and Acme's servers. At rest, files are encrypted using AES-256,
with encryption keys managed by Acme's key management service. Business
and Enterprise plans can optionally bring their own encryption key
(BYOK) for an additional layer of control over data-at-rest encryption.

## Compliance certifications
Acme maintains SOC 2 Type II certification, renewed annually via an
independent third-party audit, and is ISO 27001 certified for its
information security management system. Acme is also GDPR-compliant
for customers in the EU/UK and offers a Data Processing Addendum (DPA)
for Business and Enterprise customers on request.

## Data residency
By default, customer data is stored in the region closest to account
sign-up (US, EU, or APAC). Business and Enterprise customers can select
a specific data residency region and Acme will not move that account's
data outside the chosen region without explicit customer request.

## Employee access controls
Internal employee access to customer file content is restricted to a
small support engineering team, requires a documented support ticket
tied to the request, and is logged for audit purposes. Acme employees
cannot browse customer files without such a ticket and manager
approval.

## Incident response
Acme maintains a documented incident response process with a target of
notifying affected customers within 72 hours of confirming a security
incident that affects their data, consistent with common regulatory
notification requirements. Status updates during an active incident are
posted to Acme's public status page.

## Vulnerability disclosure and bug bounty
Acme runs a public vulnerability disclosure program and a paid bug
bounty program for qualifying security researchers. Reports can be
submitted through the security contact listed on Acme's website;
critical vulnerabilities are typically triaged within 24 hours.

## Backups and disaster recovery
Files are replicated across multiple availability zones within a
customer's chosen data residency region. Acme performs regular disaster
recovery drills and maintains a recovery point objective (RPO) of under
15 minutes and a recovery time objective (RTO) of under 4 hours for a
full regional failover.

## Account security features
Beyond two-factor authentication, Acme provides login alerts for new
device or unrecognized-location sign-ins, an active-session management
page where you can remotely sign out other devices, and — on Enterprise
plans — IP allowlisting to restrict account access to specific network
ranges.
