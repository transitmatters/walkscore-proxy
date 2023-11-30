import json
import os

import requests


def update_stations():
    with open(os.path.join("server", "chalicelib", "stations.json")) as sjson:
        stationsdict_v1 = json.load(sjson)
    stationsdict_v2 = []

    for station in stationsdict_v1:
        r_f = requests.get(f"https://api-v3.mbta.com/stops/{station['station']}")
        stop = r_f.json()

        try:
            new_station = {
                "station": station["station"],
                "stop_name": station["stop_name"],
                "address": stop["data"]["attributes"]["address"],
                "latitude": stop["data"]["attributes"]["latitude"],
                "longitude": stop["data"]["attributes"]["longitude"],
            }
            stationsdict_v2.append(new_station)
        except:
            print(f"No data for station: {station['station']}")
    
    with open(os.path.join('server', 'chalicelib', 'stationsv2.json'),"w+") as sjson:
        json.dump(obj=stationsdict_v2, fp=sjson, indent=2)
    


if __name__ == "__main__":
    update_stations()
