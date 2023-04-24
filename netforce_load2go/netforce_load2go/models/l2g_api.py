from netforce.model import Model,fields,get_model
import time
import googlemaps

API_KEY="AIzaSyAKs3alHGFG4ckYe6b0G67DbViVJX3rgV0"

class Api(Model):
    _name="l2g.api"
    _store=False

    def get_directions(self,from_loc,to_loc,context={}):
        client=googlemaps.Client(key=API_KEY)
        from_coords="%s,%s"%(from_loc["lat"],from_loc["lng"])
        to_coords="%s,%s"%(to_loc["lat"],to_loc["lng"])
        res=client.directions(from_coords,to_coords)
        if not res:
            raise Exception("Failed to get distance")
        distance=res[0]["legs"][0]["distance"]["value"]
        duration=res[0]["legs"][0]["duration"]["value"]
        return {
            "distance": distance,
            "duration": duration,
        }

Api.register()
