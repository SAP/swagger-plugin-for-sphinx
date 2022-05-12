[![REUSE status](https://api.reuse.software/badge/github.com/SAP/swagger-plugin-for-sphinx)](https://api.reuse.software/info/github.com/SAP/swagger-plugin-for-sphinx)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Swagger Plugin for Sphinx

This is handy plugin to bring [Swagger](https://swagger.io/) and [Sphinx](https://www.sphinx-doc.org/en/master/) together.

It is able to generate one or multiple swagger HTML pages with a custom configuration which host an OpenAPI specification.

## Install

Just run `pip install swagger-plugin-for-sphinx`


## Usage

First, add the plugin to the extensions list:
```python
extensions = ["swagger_plugin_for_sphinx.plugin"]
```

Then add the main configuration for swagger:
```python
swagger_present_uri = ""
swagger_bundle_uri = ""
swagger_css_uri = ""
```
These correspond to the modules explained [here](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/installation.md).
By default the latest release is used from [here](https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest).

As a last step, define the swagger configuration as followed:
```python
swagger = [
    {
        "name": "Service API",
        "page": "openapi",
        "options": {
            "url": "openapi.yaml",
        },
    }
]
```
Each item of the list will generate a new swagger HTML page.
The `name` is the HTML page name and `page` defines the file name without an extension. This needs to be included in the TOC.
The `options` are then used for the `SwaggerUIBundle` as defined [here](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md).
Please don't specify the `dom_id` since it's hardcoded in the HTML page.

In the sphinx build, a HTML page is created and put into the `_static` directory of the build.

If the specification is provided as a file, don't forget to copy it (e.g. by putting it into the `html_static_path`).

To silence the warning `toctree contains reference to nonexisting document`,, just put a dummy file with the same name as `page` into the source folder.

## Build and Publish

This project uses `poetry` as the dependency management and build tool.
To publish a new release, follow these steps:
* Update the version in the `pyproject.toml`
* Add an entry in the changelog
* Push a new tag like `vX.X.X` to trigger the release

## Support, Feedback, Contributing

This project is open to feature requests/suggestions, bug reports etc. via [GitHub issues](https://github.com/SAP/<your-project>/issues). Contribution and feedback are encouraged and always welcome. For more information about how to contribute, the project structure, as well as additional contribution information, see our [Contribution Guidelines](CONTRIBUTING.md).

## Code of Conduct

We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone. By participating in this project, you agree to abide by its [Code of Conduct](CODE_OF_CONDUCT.md) at all times.

## Licensing

Copyright 2022 SAP SE or an SAP affiliate company and swagger-plugin-for-sphinx contributors.
Please see our [LICENSE](LICENSE) for copyright and license information.
Detailed information including third-party components and their licensing/copyright information is available [via the REUSE tool](https://api.reuse.software/info/github.com/SAP/<your-project>).
