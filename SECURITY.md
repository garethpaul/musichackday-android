# Security Policy

## Supported Versions

The supported security scope for `musichackday-android` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Android Twitter App with RDIO

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/musichackday-android` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be an Android mobile application or sample. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found database, model, query, or persistence-related code; changes in those areas should receive security-focused review before merge.
- Review found secret-like configuration names that require careful review before use; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: build.gradle, gradle.properties. Dependency updates should preserve lockfiles when present and avoid introducing packages without a clear maintenance reason.
- Run `make lint`, `make test`, `make build`, and `make check` after changing Java sources, Gradle metadata, `AndroidManifest.xml`, `Constants.java.example`, or security documentation.
- The pinned Linux workflow uses a read-only, credential-free checkout and runs
  only the SDK-free static baseline without credentials, OAuth exchange, media
  downloads, Android SDK setup, or obsolete Gradle execution.
- Real `Constants.java`, Twitter/Rdio credentials, OAuth access tokens, signing keys, local properties, generated APKs, and account data should stay out of git.
- OAuth token and token-secret values should not be written to Android logs.
- The app manifest keeps backup disabled for this credential-adjacent sample baseline.
- Cached profile and album images should stay in app-private cache storage
  rather than shared external storage.
- Cached profile and album images should use SHA-256 cache filenames rather
  than short Java hashes for URL-derived names.
- Image download guards should skip invalid media URLs and recycled row image views before invoking the loader.
- The HTTP image URL guard should keep local or non-web URI schemes out of image loading.
- The HTTPS profile image guard should select Twitter's HTTPS media field and
  reject cleartext HTTP at the loader boundary.
- The album art connection guard should require HTTPS, bounded connect/read
  timeouts, generic errors, and deterministic stream/connection cleanup.
- Memory cache entry guards should prune cleared soft references and skip null cache writes.
- The OAuth callback URI guard should accept only the configured callback
  scheme and authority before exchanging Twitter verifier values.
- The OAuth callback path guard should accept only the configured callback path
  before exchanging Twitter verifier values.
- The OAuth callback verifier guard should reject missing or blank verifier
  values before requesting Twitter access tokens.
- The OAuth callback token guard should require callback tokens to match the
  active request token before requesting Twitter access tokens.
- Sanitized OAuth error logging should keep Twitter login failure logs at
  action-level messages without exception details or stack traces.
- Rdio authorization error redaction should keep cancelled SDK diagnostics out
  of application logs.
- The Rdio authorization flow guard should reject overlapping OAuth launches
  and fail closed before playback preparation when credentials are incomplete.
- The Twitter authorization origin guard should require the canonical HTTPS
  Twitter host, default port, and authenticate path before launching an
  external browser.
- Local editor metadata should stay ignored so machine-specific SDK paths,
  workspace state, and IDE module files are not committed.

## Mobile Privacy Notes

If this project requests device permissions such as location, camera, microphone, contacts, Bluetooth, health data, or local storage access, reports should describe the permission involved and whether sensitive data can be accessed, persisted, or transmitted unexpectedly. Please avoid testing against real third-party user data or accounts you do not control.

For this app, media-loading reports should include whether image download guards
prevent invalid URLs, non-HTTP(S) URI schemes, or recycled views from triggering crashes.
OAuth callback reports should include whether the OAuth callback URI guard
rejects lookalike callback hosts or schemes before verifier exchange.
OAuth callback reports should also include whether the OAuth callback path
guard rejects lookalike callback paths before verifier exchange.
OAuth callback reports should include whether the OAuth callback verifier guard
rejects missing or blank verifier values before token exchange.
OAuth callback reports should include whether the OAuth callback token guard
rejects callbacks whose token does not match the active request token.
OAuth logging reports should include whether sanitized OAuth error logging can
be bypassed to write provider exception details or stack traces.
Twitter search reports should include whether the Twitter search failure guard
can be bypassed to log raw queries, provider stack traces, or iterate a failed
result.

Twitter navigation UI thread handoff reports should include whether either OAuth
worker can launch an activity without returning to Android's main thread.
Twitter login in-flight guard reports should include whether repeated taps can
start overlapping request-token workers or replace the active callback token.

Rdio authorization flow guard reports should include whether startup can open
multiple OAuth activities or canceled and malformed results can prepare playback.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, signing material, generated Android packages, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
