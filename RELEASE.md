# Changelog

## 2026-02-20

- Support for CDN caching
- Various improvements:
  - Do not set cookies every request, only when necessary
  - Do not delete cookies when they are not set

## 2026-02-16

- Improved schema.org JSON-LD:
  - Support breadcrumbs

## 2026-03-26

- Support for Cloudflare Turnstile

## 2026-01-30

- Google login improvements:
  - Support for Google login via UserInfo API
  - Save display name from Google profile

- Improved schema.org JSON-LD:
  - Support search endpoints

## 2026-01-06

- Sitemap improvements:
  - Automatically exclude empty sitemaps
  - Support lastmod attribute in sitemaps
  - Support for dynamic sitemap generation

- Internal improvements:
  - Support FTP base directory

## 2025-11-22

Internal improvements:

- Support cache expiration for HTML content

## 2025-11-01

- Bug fixes:
  - Fix logo in email templates

## 2025-10-25

- Improved schema.org JSON-LD
- Improved Google tags

## 2025-03-23

- Support for ARIA (accessibility features)

## 2025-02-13

- Bug fixes
  - Fixed a bug in locale validation that could occur during checkout

## 2025-01-31

- Admin panel improvements:
  - Colored order statuses
  - Create orders
  - Send mass emails

## 2025-01-06

- Various improvements:
  - Improved HTML minification
  - Sensitive data is obfuscating in logging
  - Users will be prompted to set a password if they had previously always signed in using third party platforms

- Bug fixes:
  - Fixed a bug in shipment method validation that could occur during checkout
  - Fixed an incorrect redirect in the admin panel that could occur after removing a product
  - Fixed a bug in displaying product HTML that was triggered by specifc HTML content

## 2024-10-08

- Support Google tags for conversion tracking
- Updated schema.org JSON-LD for web crawlers

## 2024-09-03

- Security improvements:
  - Implementation of JSON Web Tokens
  - Protection against Cross-Site Request Forgery

- PDF generation:
  - Faster PDF generation
  - New font to support more languages
