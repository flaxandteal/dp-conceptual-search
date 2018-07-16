dp-conceptual-search
==================

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
| USER_RECOMMENDATION_ENABLED  | false                     | Enable/disable mongoDB and user recommendation engine.
| SEARCH_LEARNING_RATE         | 0.25                      | Rate at which search tries to learn about user interests (float, capped at 1.0).
| MONGO_SEARCH_DATABASE        | local                     | Default database for mongoDB.
| MONGO_BIND_ADDR              | mongodb://localhost:27017 | Default mongoDB bind address (must start with mongodb:// and end with port)
| ENABLE_PROMETHEUS_METRICS    | False                     | Enable/disable the /metircs endpoint for prometheus.

# Running

There are two options for running the server:
Use ```python manager.py``` to use the internal Sanic server, or  ```./run_gunicorn.sh``` to initialise as a 
gunicorn server (supports multi-processing for multiple workers and threads per worker).

# Testing

To run the unit tests, use: ```make test```.

# Integration

To run the integration tests, use  ```make integration-test```.

# Structure

The code is organised into three main modules:

* ```core```
* ```ons```
* ```server```

The ```core``` module implements common functionality for search, working with mongoDB, 
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

Finally, the ```server``` module hosts the ```sanic``` asynchronous HTTP server and all routes. Details of which routes are
registered and various app configurations can be found in ```server/app.py```.

### Licence

Copyright ©‎ 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE.md) for details.

This software uses the fastText library, see [LICENSE](LICENSE.fastText.md) for details.
