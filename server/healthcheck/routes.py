from sanic import Blueprint
from sanic.response import json

health_check_blueprint = Blueprint('healthcheck', url_prefix='/healthcheck')


# Define healthcheck API
@health_check_blueprint.route("/")
async def health_check(request):
    import inspect

    es_health = request.app.es_client.cluster.health()
    if inspect.isawaitable(es_health):
        es_health = await es_health

    code = 200
    if "status" not in es_health or es_health["status"] == "red":
        code = 500
    return json(es_health, code)
