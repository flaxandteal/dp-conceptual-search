dp-conceptual-search
==================

# Configuration

### Environment variales

| Environment variable         | Default                 | Description
| ---------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------
| ELASTIC_SEARCH_ASYNC_ENABLED | true                    | Specify whether to use synchronous or asynchronous Elasticsearch client.
| ELASTIC_SEARCH_SERVER        | http://localhost:9200   | URL of Elasticsearch cluster.
| ELASTIC_SEARCH_TIMEOUT       | 1000                    | Timeout of Elasticsearch requests in seconds.
| SEARCH_INDEX                 | ons*                    | The Elasticsearch index to be queried.

# Running

There are two options for running the server:
Use ```python manager.py``` to use the internal Sanic server, or  ```./run_gunicorn.sh``` to initialise as a 
gunicorn server (supports multi-processing for multiple workers and threads per worker).

# Testing

To run the tests use: ```nosetests```

### Licence

Copyright ©‎ 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE.md) for details.
