# Web Framework

This repository is a custom web framework for clients of Enlarge.

## Changelog

### 2023-08-17

Improvements:
- Fixed a bug where the GET /users endpoint would not work

### 2023-08-15

Improvements:
- Moved the generate sku endpoint to the product domain
- Refund the maximum amount when the amount is too high

### 2023-07-23

Additions:
- Add ENDPOINT_PASSWORD and ENDPOINT_ORDER for in API use

Removals:
- Remove database validation from API

Improvements:
- Add more types of validation to database

### 2023-07-19

Additions:
- Add Mypy as linter
- API automation class

Improvements:
- Billing and Shipping endpoints are using the API class
- Fixed a bug where an error was generated if a user was still in the cookies but no longer in the database

### 2023-07-15

Additions:
- Add endpoint for verification

Improvements:
- Splitted endpoints for user, user-activation and user-password
- Database objects with attributes now are non-nullable and contain a default value

### 2023-07-14

Removals:
- Dropped support for SendGrid

Improvements:
- Fixed a bug where _locale was added in URLs that don't have a locale

### 2023-07-12

Additions:
- Add more invoice and refund details to invoices and refunds

Improvements:
- Require session for document generation to ensure database connection
- Provide full SKU name in Invoice document
- Fixed a bug when it could not be determined whether an order is refundable
- Fixed a bug where the Mollie webhook URL was not generated correctly
- Fixed a bug where a list of invoices was returned while an order can have only one invoice

### 2023-07-10

Additions:
- Added a blueprint for webhooks
- Included a Mollie payment webhook endpoint

### 2023-07-09

Improvements:
- Fixed a bug in a CheckConstraint for Order that checks the coupons
- Fixed a bug where a PDF for an Order was generated with the wrong filename

### 2023-07-08

Additions:
- Added attributes property to various tables
- Added is_valid property to Verification

Removals:
- Remove html from Article and Product (use attributes instead)

Improvements:
- Invoices now have references back to the order
- Updated various foreign key on delete actions
- Relationships with an order attribute will be ordered by default
- Rename desc to description in all tables
- Rename img_url to image_url in all tables
- Rename read_html to consent_required in all tables

### 2023-07-04

Improvements:
- Fixed a bug where the shipment method id was not correctly updated
- Fixed a bug where current_user.is_authenticated() was called when the current_user was None

### 2023-07-02

Additions:
- Added custom error messages for database email and phone validation

Removals:
- Removed the Access object, instead use request callback from Flask-Login

Improvements:
- Move changelog from README.md to CHANGELOG.md
- Split EMAIL_OVERRIDE into EMAIL_TO and EMAIL_FROM
- Fixed a bug where the shipment method was not correctly loaded in POST /carts/<int:cart_id>/items
- Fixed a bug where shipment zones where not deleted if either the class or zone was deleted
- Fixed a bug where database objects where referenced with an underscore at the end, making it an invalid reference
- Fixed a bug where the sequence number for cdn auto naming was not correctly set
- Fixed a bug where the PATCH sku endpoint did not process is_visible correctly
- Fixed a bug where CDN auto naming did not extract the last sequence number correctly
- Fixed multiple bugs where objects where not correctly deleted
- Fixed multiple bugs where check constraints was not checking correctly if one of two fields where null

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