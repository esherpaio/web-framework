# Web Framework

This repository is a custom web framework for clients of Enlarge.

## Changelog

### 2023-06-09

Additions:
- Added a changelog
- Translations module
- Example config for testing purposes

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