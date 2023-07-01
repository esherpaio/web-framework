# Web Framework

This repository is a custom web framework for clients of Enlarge.

## Changelog

### 2023-07-01

Removals:
- Removed the Access object, instead use the request callback from Flask-Login

Improvements:
- Move changelog from README.md to CHANGELOG.md
- Split EMAIL_OVERRIDE into EMAIL_TO and EMAIL_FROM
- Fixed a bug where the shipment method was not correctly loaded in POST /carts/<int:cart_id>/items
- Fixed a bug where shipment zones where not deleted if either the class or zone was deleted
- Fixed a bug where database objects where referenced with an underscore at the end, making it an invalid reference
- Fixed a bug where the sequence number for cdn auto naming was not correctly set

### 2023-06-26

Additions:
- Added a guest role (in preparation for Access object removal)

Improvements:
- Rename authorize() to access_control()
- The email and password_hash on the User object are now optional (in preparation for Access object removal)
- Refactored some helper functions
- We longer store the locale in the session, this should always be derived from the URL, or database objects

### 2023-06-23

Additions:
- Modify response function
- Modify request function

Removals:
- Removed bleach

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