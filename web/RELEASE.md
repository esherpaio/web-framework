# Changelog

## v2.10.1 (2025-01-06)

- Various improvements
  - Improved HTML minification
  - Sensitive data obfuscating in logging
  - Users will be prompted to set a password if they had previously always signed in using third party platforms

- Bug fixes
  - Fixed a bug in shipment method validation that could occur during checkout
  - Fixed an incorrect redirect in the admin panel that could occur after removing a product
  - Fixed a bug in displaying product HTML that was triggered by specifc HTML content

## v2.10.0 (2024-10-08)

- Support Google tags for conversion tracking
- Updated schema.org JSON-LD for web crawlers

## v2.9.0 (2024-09-03)

- Security improvements
  - Implementation of JSON Web Tokens
  - Protection against Cross-Site Request Forgery

- PDF generation
  - Faster PDF generation
  - New font to support more languages
