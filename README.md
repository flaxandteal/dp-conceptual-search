dp-conceptual-search
==================

# Configuration

### Environment variables

| Environment variable         | Default                   | Description
| ---------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------
| TESTING                      | false                     | Configures the app for unit testing.
| ELASTIC_SEARCH_ASYNC_ENABLED | true                      | Specify whether to use synchronous or asynchronous Elasticsearch client.
| ELASTIC_SEARCH_SERVER        | http://localhost:9200     | URL of Elasticsearch cluster.
| ELASTIC_SEARCH_TIMEOUT       | 1000                      | Timeout of Elasticsearch requests in seconds.
| SEARCH_INDEX                 | ons                       | The Elasticsearch index to be queried.
| BIND_HOST                    | 0.0.0.0                   | The host to bind to.
| BIND_PORT                    | 5000                      | The port to bind to.
| SANIC_WORKERS                | 1                         | Number of Sanic worker threads.
| ENABLE_PROMETHEUS_METRICS    | false                     | Enable/disable the /metircs endpoint for prometheus.
| COLOURED_LOGGING_ENABLED     | false                     | Enable/disable coloured logging.
| PRETTY_LOGGING               | false                     | Enable/disable JSON formatting for logging.
| LOG_LEVEL                    | INFO                      | Log level (INFO, DEBUG, or ERROR)

# Install

To install locally (not recommended), run ```make```. The code requires python3.6, and it is recommended that you setup 
a [virtual environment](https://docs.python.org/3/library/venv.html).
Alternatively (preferred approach), you can use the supplied Dockerfile to run in a container. When running with 
conceptual search and user recommendation enabled, the simplest approach is to use ```docker-compose``` with the
```docker-compose.yml``` provided (run `docker-compose build` before `docker-compose up`). Note that for conceptual search,
 Elasticsearch requires a [plugin for vector scoring](https://github.com/ONSDigital/fast-elasticsearch-vector-scoring).
The `docker-compose.yml` file provided will pull a custom Elasticsearch 2.4.4 image with this plugin pre-installed when 
working locally (be sure to switch off any instances of Elasticsearch that might already be running first).  

# Running

There are two options for running the server:
Use ```python manager.py``` to use the internal Sanic server, or  ```./run_gunicorn.sh``` to initialise as a 
gunicorn server (supports multi-processing for multiple workers and threads per worker). By default, the service 
provides APIs which only mimic the search functionality of babbage. To enable conceptual search (vector scoring), you
will need to set the environment variable ```CONCEPTUAL_SEARCH_ENABLED=true``` and have the appropriate models available
on disk. This repository comes with a [word2vec embeddings model](ml/data/word2vec/ons_supervised.vec) for spell checking.

# Indexing content

Make sure you have checked out the `feature/vector_embedding_dp_fasttext` branch of `zebedee-reader` and have 
[`dp-fasttext`](https://github.com/ONSdigital/dp-fasttext) running in order to generate the embedding vectors.

# Swagger

The swagger spec can be found in ```swagger.yaml```

# Testing

To run the unit tests, use: ```make test```.

# Structure

The code is organised into the following modules:

* ```search```
* ```ons```
* ```app```
* ```api```
* ```config```
* ```unit```

The ```search``` module implements common functionality for search, working with mongoDB, 
loading (un)supervised word embedding modules, spell checking, and user / session tracking. The core recommendation
engine is also implemented here, and is responsible for updating user session vectors using the supplied models.

The ```ons``` module contains code specific to the ONS search implementation, such as Elasticsearch queries, index names, 
content types, sort fields, filter functions, type filters, and pagination.

All routes (handlers) are defined in the ```api``` package (in files called ```routes.py```).

The ```Sanic``` HTTP server is defined in ```app/app.py```. Here we register all blueprints (routes) and configure
app wide logging.

App wide configs are defined in ```config/config.py``` and collected under a single section in ```config/__init__.py```.

Finally, all unit tests can be found in the ```unit``` package. See the ```test``` make target and ```manager.py``` for information
on how to run the tests.

### Licence

Copyright ©‎ 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE.md) for details.

This software uses the fastText library, see [LICENSE](fasttext/LICENSE.md) for details.
