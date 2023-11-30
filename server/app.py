import json
import os
from chalice import Chalice, CORSConfig, ConvertToMiddleware
from datadog_lambda.wrapper import datadog_lambda_wrapper
import requests

app = Chalice(app_name="walkscore-proxy")

localhost = "localhost:3000"
TM_CORS_HOST = os.environ.get("TM_CORS_HOST", localhost)

cors_config = CORSConfig(allow_origin=f"https://{TM_CORS_HOST}", max_age=3600)

if TM_CORS_HOST != localhost:
    app.register_middleware(ConvertToMiddleware(datadog_lambda_wrapper))


@app.route("/api/walkscore/{station_key}", cors=cors_config)
def get_walkscore(station_key):
    with open(os.path.join("chalicelib", "stations.json")) as sjson:
        stations = json.load(sjson)
    station = next((x for x in stations if x['station'] == station_key), None)

    if (station is not None):
        # Call Walkscore API
        walkscore_response = requests.get(
            f"https://api.walkscore.com/score?format=json&address={station['address']}&lat={station['latitude']}&lon={station['longitude']}&bike=1&wsapikey={os.environ.get('WALKSCORE_API_KEY')}"
        )
        return json.dumps(walkscore_response.json(), indent=4, sort_keys=True, default=str)
    return None
