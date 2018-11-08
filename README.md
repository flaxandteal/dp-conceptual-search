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
| LOG_LEVEL                    | INFO                      | Log level (INFO, DEBUG, TRACE or ERROR)

# Install

To install locally (not recommended), run ```make```. The code requires python3.6, and it is recommended that you setup 
a [virtual environment](https://docs.python.org/3/library/venv.html).
Alternatively (preferred approach), you can use the supplied Dockerfile to run in a container. When running with 
conceptual search and user recommendation enabled, the simplest approach is to use ```docker-compose``` with the
```docker-compose.yml``` provided to bring up dedicated instances of mongoDB and Elasticsearch. Note that for conceptual
search, the latter requires a [plugin for vector scoring](https://github.com/sully90/fast-elasticsearch-vector-scoring).  

# Running

There are two options for running the server:
Use ```python manager.py``` to use the internal Sanic server, or  ```./run_gunicorn.sh``` to initialise as a 
gunicorn server (supports multi-processing for multiple workers and threads per worker). By default, the service 
provides APIs which only mimic the search functionality of babbage. To enable conceptual search (vector scoring), you
will need to set the environment variable ```CONCEPTUAL_SEARCH_ENABLED=true``` and have the appropriate models available
on disk. This repository comes with the [full word2vec embeddings model](ml/data/word2vec/ons_supervised.vec) and a 
*test* [supervised model](unit/ml/test_data/supervised_models/ons_supervised.bin).

# Swagger

The swagger spec can be found in ```swagger.yaml```

# Testing

To run the unit tests, use: ```make test```.

# Structure

The code is organised into four main modules:

* ```search```
* ```ons```
* ```app```
* ```api```

The ```search``` module implements common functionality for search, working with mongoDB, 
loading (un)supervised word embedding modules, spell checking, and user / session tracking. The core recommendation
engine is also implemented here, and is responsible for updating user session vectors using the supplied models.

The ```ons``` module contains code specific to the ONS search implementation, such as Elasticsearch queries, index names, 
content types, sort fields, filter functions, type filters, and pagination. Any modifications to the queries being 
executed in either the vanilla search engine (babbage replica), or the new conceptual search engine, should
be made in this module. The implementation of both search engines follow the same pattern:

1. Define methods to build queries in a ```queries.py``` file, using the ```elasticsearch_dsl``` module.
2. Define  a ```SearchEngine``` class which extends the ```AbstractSearchClient``` (see ```ons/search/search_engine.py```)
3. Define utilty methods on  ```SearchEngine``` class as required, following the clone patten as seen in the 
```ons/search/search_engine.SearchEngine``` class
4. Manipulate ```SearchEngine``` class in server routes to execute queries.

To implement conceptual search, we simply extend the ```ons/search/search_engine.SearchEngine``` class and redefine the 
original content query (see ```ons/search/queries.py```) to take advantage of our pre-trained models and
indexed embedding vectors (see ```ons/search/conceptual/queries.py``` and ```ons/search/conceptual/search_engine.py```).
As such, all the core logic for pagination, field highlighting, aggregations, sorting and type filtering need only be implemented once
in ```ons/search/search_engine.AbstractSearchClient```.

Finally, the ```app``` and ```api``` modules host the ```sanic``` asynchronous HTTP server and all routes. Details of which routes are registered and various app configurations can be found in ```app/app.py```.

### Licence

Copyright ©‎ 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE.md) for details.

This software uses the fastText library, see [LICENSE](LICENSE.fastText.md) for details.
