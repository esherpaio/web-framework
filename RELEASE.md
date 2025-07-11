# Changelog

## v0.10.6 (2025-03-23)

- Support for ARIA (accessibility features)

## v0.10.3 (2025-02-13)

- Bug fixes
  - Fixed a bug in locale validation that could occur during checkout

## v0.10.2 (2025-01-31)

- Admin panel improvements
  - Colored order statuses
  - Create orders (BETA)
  - Send mass emails (BETA)

## v0.10.1 (2025-01-06)

- Various improvements
  - Improved HTML minification
  - Sensitive data is obfuscating in logging
  - Users will be prompted to set a password if they had previously always signed in using third party platforms

- Bug fixes
  - Fixed a bug in shipment method validation that could occur during checkout
  - Fixed an incorrect redirect in the admin panel that could occur after removing a product
  - Fixed a bug in displaying product HTML that was triggered by specifc HTML content

## v0.10.0 (2024-10-08)

- Support Google tags for conversion tracking
- Updated schema.org JSON-LD for web crawlers

## v0.9.0 (2024-09-03)

- Security improvements
  - Implementation of JSON Web Tokens
  - Protection against Cross-Site Request Forgery

- PDF generation
  - Faster PDF generation
  - New font to support more languages
