# Web Framework

This repository is a custom web framework for clients of Enlarge.

## Changelog

### 2023-06-23

Improvements:
- API
    - Added more attributes to be POSTed or PATCHed
    - More custom error messages
    - Modify response function
- API /users*
    - Return a list in GET /users, before it was a single dict
    - Slightly enhanced security by using a better flow on PATCH /users/id
- API /carts*
    - Return a list in GET /carts, before it was a single dict
    - Remove changing stuff in the session: it should not be related to the API

### 2023-06-20

Improvements:
- More meta tags
- Automatic generation of meta tags
- Add img_url to Page database scheme
- Add translations to Makefile
- FSOs renaming

### 2023-06-19

Improvements:
- Remove optional from config variables
- Support for sending attachments over SMTP
- Simplified mailing functions

Additions:
- The email method must be explicitly mentioned in env var EMAIL_METHOD
- Unit tests

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