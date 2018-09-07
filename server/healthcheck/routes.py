from sanic import Sanic, Blueprint
from sanic.request import Request
from sanic.response import json

health_check_blueprint = Blueprint('healthcheck', url_prefix='/healthcheck')


def mongo_health(request: Request) -> (dict, int):
    from core.utils import check_for_connection_error

    current_app: Sanic = request.app
    host: str = current_app.config.get('MONGO_DEFAULT_HOST')
    port = current_app.config.get('MONGO_DEFAULT_PORT')

    port: int = int(port)

    client = None
    err = check_for_connection_error(host, port)

    if err is None:
        try:
            import pymongo
            client = pymongo.MongoClient(host=host, port=port)
            info = client.server_info()
            code = 200
        finally:
            if client is not None:
                client.close()
    else:
        info = {"mongoDB": err}
        code = 500

    return info, code


async def elastic_search_health(request: Request) -> (dict, int):
    """
    Health check method for elasticsearch
    :param request:
    :return:
    """
    import inspect
    from elasticsearch.exceptions import ConnectionError

    current_app: Sanic = request.app
    code = 200

    try:
        info = current_app.es_client.cluster.health()
        if inspect.isawaitable(info):
            info = await info

            if "status" not in info or info["status"] == "red":
                code = 500
    except ConnectionError as err:
        info = {"elasticsearch": err}
        code = 500

    return info, code


# Define healthcheck API
@health_check_blueprint.route("/", strict_slashes=True)
async def health_check(request: Request):
    from config_core import USER_RECOMMENDATION_ENABLED

    health = {}
    code = 200

    es_health, es_code = await elastic_search_health(request)

    if es_code == 200:
        health['elasticsearch'] = 'available'
    else:
        health['elasticsearch'] = 'unavailable'
        code = 500

    if USER_RECOMMENDATION_ENABLED:
        mdb_health, mdb_code = mongo_health(request)

        if mdb_code == 200:
            health['mongoDB'] = 'available'
        else:
            health['mongoDB'] = 'unavailable'
            # Return a 202 ACCEPTED (certain parts of the app will continue to
            # work as normal)
            code = 202

    return json(health, code)
