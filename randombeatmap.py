import requests
import random
import time
from bs4 import BeautifulSoup
import json
import mypersonalib

mypersonalib.initcookie()

desired_mode = 0 # can be 0 (osu) 3 (mania) 1 (taiko) 2 (catch) or None
mode_filter = True # this is seperate from the other filters either True or False

ammount_of_valid_maps = 10 # how much valid maps till program end?
desired_od = None
desired_hp = None
desired_ar = None
desired_bpm = None
desired_length = None # length in seconds
desired_star_rating = None
comparison_type = None # decides if these desired variables should be not matching
# or exact or lte (lower than or equal) or gte (greater than or  equal) None (the type) will disable
# the filter


def check_value(value, desired_value, comparison_type): # idea of a helper function  by AI
    if desired_value is None:
        return True
    if comparison_type == "exact":
        return value == desired_value
    elif comparison_type == "lte":
        return value <= desired_value
    elif comparison_type == "gte":
        return value >= desired_value
    return False 

i =0

while i < ammount_of_valid_maps:
    time.sleep(2)
    beatmapset_id = random.randint(0,1000000)
    beatmap_link = f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}"
    
    response = requests.get(beatmap_link)
    if response.status_code == 404:

        print(f"map {beatmapset_id} not found")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        script_tag = soup.find("script", id="json-beatmapset")        
        parsed_data = json.loads(script_tag.string)
        artist = parsed_data.get("artist")
        song_name = parsed_data.get("title")
        for beatmaps in (parsed_data.get("beatmaps")):
            ar = beatmaps.get("ar")
            bpm = beatmaps.get("bpm")
            od = beatmaps.get("accuracy")
            hp = beatmaps.get("drain")
            length = beatmaps.get("total_length")
            star = beatmaps.get("difficulty_rating")
            mode_int = beatmaps.get("mode_int")

            if mode_filter:
                if desired_mode is not None:
                    if mode_int != desired_mode:
                        continue

            if (check_value(ar, desired_ar, comparison_type) and
                check_value(bpm, desired_bpm, comparison_type) and
                check_value(od, desired_od, comparison_type) and
                check_value(hp, desired_hp, comparison_type) and
                check_value(length, desired_length, comparison_type) and
                check_value(star, desired_star_rating, comparison_type)):
                
                i+=1
                print(f"Valid map found: {beatmap_link}")
                #os.startfile(beatmap_link)
                mypersonalib.downloadosumap(beatmapset_id, artist, song_name)
                break
