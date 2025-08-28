import json
import os
from chalice import Chalice, CORSConfig, ConvertToMiddleware
from datadog_lambda.wrapper import datadog_lambda_wrapper
import requests
from dynamodb_cache import DynamoDBCache

app = Chalice(app_name="walkscore-proxy")

localhost = "localhost:3000"
TM_CORS_HOST = os.environ.get("TM_CORS_HOST", localhost)

if TM_CORS_HOST != localhost:
    cors_config = CORSConfig(allow_origin=f"https://{TM_CORS_HOST}", max_age=3600)
    app.register_middleware(ConvertToMiddleware(datadog_lambda_wrapper))
else:
    cors_config = CORSConfig(allow_origin=f"http://{TM_CORS_HOST}", max_age=3600)


@app.route("/api/walkscore/{station_key}", cors=cors_config)
def get_walkscore(station_key):
    with open(os.path.join("chalicelib", "stations.json")) as sjson:
        stations = json.load(sjson)
    station = next((x for x in stations if x["station"] == station_key), None)

    if station is not None:
        cache_instance = DynamoDBCache()
        cache = cache_instance.get(key=station["station"])
        if cache:
            print("returning from the cache")
            return json.dumps(cache)
        # Call Walkscore API
        walkscore_response = requests.get(
            f"https://api.walkscore.com/score?format=json&address={station['address']}&lat={station['latitude']}&lon={station['longitude']}&bike=1&wsapikey={os.environ.get('WALKSCORE_API_KEY')}"
        )
        data = json.dumps(walkscore_response.json(), indent=4, sort_keys=True, default=str)
        cache_instance.set(station["station"], data)
        return data
    return None
