# Security Policy

## Scope

This repository contains public documentation and small verification utilities.
It does not contain the operational system or the sealed private evidence.

Security-sensitive reports must not be opened as public issues. Use GitHub's
[private vulnerability reporting form](https://github.com/Atanasseri/agentic-engineering-assurance-system/security/advisories/new)
and provide only the minimum information needed to locate the concern. If the
form is unavailable, do not disclose the report publicly; wait until the owner
enables the private channel.

## Report immediately

- a credential, token, private key, or authentication artifact;
- a private repository locator or inaccessible internal URL;
- an operating-environment path, host, account, session, or process identifier;
- personal or customer information;
- content that reconstructs a private decision or model conversation; or
- an integrity mismatch between a published asset and its recorded digest.

If sensitive information appears in Git history, removing it from the latest
commit is not sufficient. Publication must stop while the affected history,
credentials, release, and downstream archives are assessed.

## Supported versions

Only the most recent signed public release is actively maintained. Older
releases remain historical records and may contain explicitly documented
limitations.
