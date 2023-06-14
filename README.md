# Web Framework

This repository is a custom web framework for clients of Enlarge.

## Changelog

### 2023-06-14

Improvements:
- Change the way emails are send over the API

Deprecated:
- Remove pycodestyle

### 2023-06-12

Added:
- Utility to synchronize translations

Improvements:
- Created all translations in EN and NL

### 2023-06-10

Improvements:
- Mail automatically recognizes language

### 2023-06-09

Additions:
- A changelog
- Translations module
- Example config

Deprecated:
- CACHE_MIMETYPE is removed due to big variations between projects

Improvements:
- New way to load config
    - No need to call load_config() anymore
    - Config variables are cached
    - Better support for validation
- Emails
    - Possibility to hide the unsubscribe element in an email
    - The render_email() function kwargs have been changed

Bugs:
- APP_DEBUG was not correctly loaded as a boolean