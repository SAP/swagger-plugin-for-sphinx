# Changelog

## 6.0.0
* Removed support for sphinx 6.x
* Removed support for python 3.9

## 5.2.0

* Add support for python 3.14

## 5.1.3

* Pass the Swagger UI options also for inline rendering.

## 5.1.2

* Added missing dependency on `typing-extensions`

## 5.1.1

* Fixed a bug related to referencing a specification from a parent
  directory of the Sphinx source directory, such as when documentation
  is co-located with source code.

  Before this fix, when a specification was several subdirectories
  from the documentation, the specification could be copied to
  a parent directory of the build HTML output and prevent the display
  of the specification.

  With this fix, deeply nested specifications (`../../../../openapi.yaml`)
  have the `..` values that are parents of the Sphinx source directory
  replaced with the text `dot-dot`. This fix ensures that deeply
  nested specifications are copied to a subdirectory of the `_static`
  directory in the HTML output.

## 5.1.0

* Refactored copying the specification to the HTML output and
  referencing the path to the specification in the HTML page.
* Preserves the source directory structure like `docs/api/foo/openapi.yaml`
  and `docs/api/bar/openapi.yaml` so that different files can use
  the same file name.

## 5.0.3

* Fixed an issue causing a spec to be linked incorrectly when the `dirhtml` builder is used.

## 5.0.2

* Fixed an issue causing a spec to be linked incorrectly when the source document is in a subfolder
  but the referenced spec is in another one

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
