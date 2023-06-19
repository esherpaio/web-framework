# Web Framework

This repository is a custom web framework for clients of Enlarge.

## Changelog

### 2023-06-19

Improvements:
- Remove optional from config variables

Additions:
- The email method must be explicitly mentioned in env var EMAIL_METHOD

### 2023-06-18

Improvements:
- Email API small bug fixes

Additions:
- Email template for Mertens Keukenambacht

### 2023-06-16

Improvements:
- Loading integers from environment variables bug fix

Additions:
- Email over SMTP
- EMAIL_OVERRIDE as config variable

### 2023-06-15

Improvements:
- Issues with % symbol in translations fixed

### 2023-06-14

Removals:
- Remove pycodestyle

Improvements:
- Change the way emails are send over the API

### 2023-06-12

Improvements:
- Created all translations in EN and NL

Additions:
- Utility to synchronize translations

### 2023-06-10

Improvements:
- Mail automatically recognizes language

### 2023-06-09

Removals:
- CACHE_MIMETYPE is removed due to big variations between projects

Improvements:
- New way to load config
    - No need to call load_config() anymore
    - Config variables are cached
    - Better support for validation
- Emails
    - Possibility to hide the unsubscribe element in an email
    - The render_email() function kwargs have been changed
- APP_DEBUG was not correctly loaded as a boolean

Additions:
- A changelog
- Translations module
- Example config