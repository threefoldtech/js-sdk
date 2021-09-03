# OpenAPI and Swagger-UI

This directory contains [OpenAPI v3 specification](https://swagger.io/docs/specification/about/) and [swagger UI](https://github.com/swagger-api/swagger-ui) files for VDC controller API

## Specifications

The following are the summary of current components that describe current API:

- Schemas: describing response/request schemas and errors
- Examples: describing response/request examples
- Paths: describing all api endpoints and referencing schemas, errors and examples.

In case of any updates, these different components need to be updated accordingly.

There are some helpful online tools to generate YAML examples and schemas from JSON response or request bodies:

* [Swagger definition generator](https://roger13.github.io/SwagDefGen/): It's for v2, but the only difference is the "definition" key, which should be replaced by "properties".
* [JSON to YAML converter](https://codebeautify.org/json-to-yaml): which helps generating YAML examples from JSON.

## Base URL and Authentication

The API is served at `/vdc_dashboard/api/controller`, with basic authentication of VDC name and secret as username/password.

## Swagger UI

Swagger UI uses current specification file `openapi.yaml`, and is served at `/vdc_dashboard/apidoc`, API endpoints can be tested directly (don't forget to authorize first).

## Generating clients

[swagger-codegen](https://github.com/swagger-api/swagger-codegen) can be used to generate clients, for example to generate `python` client:

```
mkdir pyclient
java -jar /path/to/swagger-codegen-cli.jar generate -l python -i /path/to/swagger/openapi.yaml
```

* `/path/to/swagger-codegen-cli.jar` is the full path of `swagger-codegen-cli`.
* `/path/to/swagger/openapi.yaml` is the full path of openapi.yaml inside this directory.
