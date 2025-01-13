[![REUSE status](https://api.reuse.software/badge/github.com/SAP/swagger-plugin-for-sphinx)](https://api.reuse.software/info/github.com/SAP/swagger-plugin-for-sphinx)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Swagger Plugin for Sphinx

This is a handy plugin to bring [Swagger](https://swagger.io/) and [Sphinx](https://www.sphinx-doc.org/en/master/) together.

It can generate one or multiple swagger HTML pages with a custom configuration that hosts an OpenAPI specification.

## Install

Just run `pip install swagger-plugin-for-sphinx`

## Usage

### Enable the Plugin

First, add the plugin to the extensions list:

```python
extensions = ["swagger_plugin_for_sphinx"]
```

### Global Configuration

Swagger uses two JavaScript and one CSS file to render the output.
These can be set in ``conf.py``:

```python
swagger_present_uri = ""
swagger_bundle_uri = ""
swagger_css_uri = ""
```

These correspond to the modules explained [here](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/installation.md).
By default, the latest release is used from [here](https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest).

### Directive

To include a Swagger API specification into an HTML page specify the `swagger-plugin` directive
and the relative path to the specification:

```code
.. swagger-plugin:: path/to/spec.yaml
```

The spec is automatically copied into the `html_static_path`.

The directive supports the following options

* `id`: specifies an unique id for the specifiction per page (see below)
* `full-page`: if set, all other content on the page is dropped and only the swagger part is rendered
* `page-title`: the name of the HTML page if `full-page` is used
* `swagger-options`: JSON string which is passed to swagger to enable additional options as described
    [here](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md)


By default, the directive creates a `<div>` element with the ID `swagger-ui-container`.
If you put more than one `swagger-plugin` directive in a file, specify unique IDs:

```code
.. swagger-plugin:: path/to/one.yaml
   :id: spec-one

.. swagger-plugin:: path/to/two.yaml
   :id: spec-two
```

## Build and Publish

This project uses `setuptools` as the dependency management and build tool.
To publish a new release, follow these steps:
* Update the version in the `pyproject.toml`
* Add an entry in the changelog
* Push a new tag like `vX.X.X` to trigger the release

## Support, Feedback, Contributing

This project is open to feature requests/suggestions, bug reports etc., via [GitHub issues](https://github.com/SAP/<your-project>/issues). Contribution and feedback are encouraged and always welcome. For more information about how to contribute, the project structure, as well as additional contribution information, see our [Contribution Guidelines](CONTRIBUTING.md).

## Code of Conduct

We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone. By participating in this project, you agree to abide by its [Code of Conduct](CODE_OF_CONDUCT.md) at all times.

## Licensing

Copyright 2024 SAP SE or an SAP affiliate company and swagger-plugin-for-sphinx contributors.
Please see our [LICENSE](LICENSE) for copyright and license information.
Detailed information including third-party components and their licensing/copyright information is available [via the REUSE tool](https://api.reuse.software/info/github.com/SAP/<your-project>).
