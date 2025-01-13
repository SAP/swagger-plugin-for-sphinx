# Changelog

## 5.0.1

* Fix some errors when the spec is in a subdirectory

## 5.0.0

This release combines the previous three way into one directive streamlining the project

* Removed the `swagger` configuration from `conf.py` (however, the `swagger_*` configuration remain).
  Use the `swagger-plugin` directive with the `full-page` option to active the same
* Removed the `inline-swagger` directive.
  Use the `swagger-plugin` directive instead

## 4.1.0

* Add a `swagger-plugin` directive:

  * Automatically copy the specification YAML file to the HTML static path.
  * Insert the Swagger JavaScript and CSS tags in the `<head>` element of the HTML page.
  * Does not require the `swagger` configuration in the `conf.py` file.

## 4.0.0

* Add support for python 3.13
* Drop support for python 3.8

## 3.6.0

* Add support for sphinx 8

## 3.5.0

* No new features but a switch of the way this package is released

## 3.4.0

* Official support file paths for `swagger_present_uri`, `swagger_bundle_uri` and `swagger_css_uri`
* Remove an unnecessary download of `swagger_present_uri`, `swagger_bundle_uri` and `swagger_css_uri`

## 3.3.0

* Support python 3.12

## 3.2.0

* Support for inline swagger pages

## 3.1.0

* Support Sphinx 7

## 3.0.0

* Make ``swagger_plugin_for_sphinx.plugin`` private
* Remove ``swagger_plugin_for_sphinx.__version__``
* The module can now be used as the extension name, so instead of using
  ``swagger_plugin_for_sphinx.plugin`` use ``swagger_plugin_for_sphinx``

## 2.0.0

* Support sphinx 6.x
* Add official support for python 3.11
* Remove support for python 3.7
* Remove support for sphinx 4.x and 5.x

## 1.2.0

* Require at least python 3.7.2
* Support sphinx 5.x

## 1.1.0

* internal change from ``os.path`` to ``pathlib``
* Marked the project as stable

## 1.0.0

Initial release
