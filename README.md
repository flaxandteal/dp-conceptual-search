dp-conceptual-search
==================

# TODO

* Test randomness of word vectors upon training of new model
* Install NLP plugin and add entities search to base content query

# Known Issues
* Pagination results in repeated update of User session vectors

# Configuration

### Environment variables

| Environment variable         | Default                   | Description
| ---------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------
| SEARCH_CONFIG                | development               | Specifies which config_*.py file to use.
| ELASTIC_SEARCH_ASYNC_ENABLED | true                      | Specify whether to use synchronous or asynchronous Elasticsearch client.
| ELASTIC_SEARCH_SERVER        | http://localhost:9200     | URL of Elasticsearch cluster.
| ELASTIC_SEARCH_TIMEOUT       | 1000                      | Timeout of Elasticsearch requests in seconds.
| SEARCH_INDEX                 | ons*                      | The Elasticsearch index to be queried.
| BIND_HOST                    | 0.0.0.0                   | The host to bind to.
| BIND_PORT                    | 5000                      | The port to bind to.
| CONCEPTUAL_SEARCH_ENABLED    | false                     | Enable/disable conceptual search (requires fastText models).
| SEARCH_LEARNING_RATE         | 0.25                      | Rate at which search tries to learn about user interests (float, capped at 1.0).
| MONGO_SEARCH_DATABASE        | local                     | Default database for mongoDB.
| MONGO_BIND_ADDR              | mongodb://localhost:27017 | Default mongoDB bind address (must start with mongodb:// and end with port)

# Running

There are two options for running the server:
Use ```python manager.py``` to use the internal Sanic server, or  ```./run_gunicorn.sh``` to initialise as a 
gunicorn server (supports multi-processing for multiple workers and threads per worker).

# Testing

To run the tests use: ```make test```

### Licence

Copyright ©‎ 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE.md) for details.
