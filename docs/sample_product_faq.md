# Acme Cloud Storage — Product FAQ

## How much storage do I get on the free plan?
The free plan includes 5GB of storage and supports files up to 2GB each.
Paid plans start at 100GB on Pro, 1TB on Business, and unlimited pooled
storage on Enterprise (subject to fair-use review for accounts storing
several hundred terabytes or more).

## Can I share a folder with someone who doesn't have an Acme account?
Yes. Any folder can be shared via a public link. The recipient can view
and download files without creating an account, but they cannot upload
or edit unless you invite them as a collaborator with an Acme account.
Link sharing can be restricted to "anyone with the link," "people in
your organization," or specific email addresses, and can be set to
expire automatically after a chosen number of days.

## Does Acme support two-factor authentication?
Yes, via an authenticator app (TOTP) or SMS. Two-factor authentication
can be enabled from Account Settings > Security, and is required by
default for all Business and Enterprise plans. Enterprise admins can
also enforce 2FA org-wide and block SMS as a fallback method, requiring
an authenticator app only.

## What happens to my files if I downgrade from a paid plan?
If your paid plan is storing more data than your new plan's limit, your
account is put into read-only mode: you can download and delete files,
but you cannot upload new ones, until your usage is back under the new
plan's storage limit. Files are never deleted automatically because of
a downgrade.

## Is there an API?
Yes, a REST API is available on Business and Enterprise plans, documented
at a separate developer portal. The free and Pro plans do not include
API access. API requests are rate-limited to 1,000 requests per minute
per account on Business, and can be raised on Enterprise by request.

## Is there a desktop sync client?
Yes, available for Windows, macOS, and most major Linux distributions.
The sync client mirrors a chosen local folder to your Acme storage and
supports selective sync, so you can choose to keep only certain
subfolders available offline on a given device.

## Is there a mobile app?
Yes, for iOS and Android. The mobile app supports automatic camera-roll
backup, offline access to files you've pinned, and can be configured to
only back up over Wi-Fi to avoid mobile data charges.

## Does Acme keep file version history?
Yes. Every plan keeps at least 30 days of version history for every
file, so you can restore an earlier version or recover a file that was
overwritten. Business and Enterprise plans extend this to 180 days, and
Enterprise can request unlimited version history as an add-on.

## What happens to deleted files?
Deleted files go to a Trash folder and are recoverable for 30 days on
Free and Pro plans, and 90 days on Business and Enterprise, after which
they are permanently purged and cannot be recovered by Acme support.

## Can I recover a file after Trash has been emptied manually?
No. Emptying Trash manually is immediate and irreversible — Acme does
not retain a further backup copy of manually-purged files.

## Are there team or workspace features?
Yes. Business and Enterprise plans include shared team workspaces with
role-based permissions (viewer, editor, admin), a shared team folder
structure separate from personal storage, and an admin console showing
storage usage and activity per member.

## Does Acme support single sign-on (SSO)?
SSO via SAML 2.0 is available on Enterprise plans only, and can be
configured with most major identity providers. Business and lower plans
support standard email/password or Google/Microsoft account login, but
not SAML-based SSO.

## Can I export all of my data if I want to leave Acme?
Yes. Account Settings > Data Export lets you request a full export of
your files and folder structure as a single downloadable archive. Large
exports (multiple terabytes) may take up to 48 hours to prepare and are
made available via a temporary download link that expires after 7 days.

## Does Acme integrate with other tools?
Yes — native integrations exist for several common productivity and
office-suite tools, plus a public API for building custom integrations
on Business and Enterprise plans. A full list of built-in integrations
is available from the Integrations tab in account settings.

## Is there a limit on how much bandwidth I can use?
Free and Pro plans have no hard bandwidth cap under normal usage, but
extremely high sustained download volumes may be temporarily throttled
to protect service quality for other users. Business and Enterprise
plans are not subject to this throttling.

## Can I set a custom domain for shared links?
Custom domains for shared links are available on Enterprise plans, so
public links can be served from your own company domain instead of
Acme's default sharing domain.
