# OS Hub API - V1 Design Spec

This GitHub repository houses both the OpenAPI specifications and RESTful API design best practices used for making changes and implementing new features for the Target API. This ensures consistency and quality in API modifications and enhancements.

## Before you begin

This project uses the latest version of the [OpenAPI Specification](https://swagger.io/specification/) and [JSON Schema](https://json-schema.org/learn/getting-started-step-by-step). We recommend familiarizing yourself with it if you are not already.

## Getting started

This repository uses [Docker](https://www.docker.com/) for local development, so:

1. Make sure you have [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

2. Then run the following command in your `terminal`:

  ```bash
  docker compose up -d
  ```

3. After running the command, you'll be able to access the rendered specification on [http://localhost:8090/](http://localhost:8090/).

4. Edit the [openapi.yaml](/openapi.yaml) file to add new API endpoints and see them immediately reflected in the browser interface.

5. All of the `schemas` are located inside the [/schemas](/schemas/) directory and referenced inside the [openapi.yaml](/openapi.yaml) file.
