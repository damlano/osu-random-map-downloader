import requests
import random
import time
from bs4 import BeautifulSoup
import json
import helperlib

helperlib.initcookie()

desired_mode = 0 # can be 0 (osu) 3 (mania) 1 (taiko) 2 (catch) or None
mode_filter = True  # either True or False

amount_of_valid_maps = 1  # how many valid maps before program ends?
desired_od = None
desired_hp = None
desired_ar = None
desired_bpm = None
desired_cs = None  # for mania this is the number of keys
desired_length = None  # length in seconds
desired_star_rating = None
desired_status = None # put a string here with graveyard ranked or loved depends what oyu want

# GTE = Greater than equal 
comparison_types = {# LTE = Lower than equal
    "ar": None,# exact = exact
    "bpm": None,# None to disable (none the type)
    "od": None,
    "hp": None,
    "length": None,
    "cs": None,
    "star": None,
    "status": None,
}

def check_value(value, desired_value, comparison_type):
    if desired_value is None or comparison_type is None:
        return True
    if comparison_type == "exact":
        return value == desired_value
    elif comparison_type == "lte":
        return value <= desired_value
    elif comparison_type == "gte":
        return value >= desired_value
    return False

def get_valid_map():
    time.sleep(1)
    beatmapset_id = random.randint(0, 2183201)
    beatmap_link = f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}"
    response = requests.get(beatmap_link)
    if response.status_code == 404:
        return get_valid_map()
    return response

i = 0

while i < amount_of_valid_maps:
    response = get_valid_map()
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", id="json-beatmapset")
        
        if script_tag is None or not script_tag.string:
            continue
        
        parsed_data = json.loads(script_tag.string)
        artist = parsed_data.get("artist")
        song_name = parsed_data.get("title")
        
        for beatmap in parsed_data.get("beatmaps", []):
            ar = beatmap.get("ar")
            bpm = beatmap.get("bpm")
            od = beatmap.get("accuracy")
            hp = beatmap.get("drain")
            length = beatmap.get("total_length")
            star = beatmap.get("difficulty_rating")
            mode_int = beatmap.get("mode_int")
            cs = beatmap.get("cs")
            status = beatmap.get("status")
            if mode_filter and desired_mode is not None and mode_int != desired_mode:
                continue
            
            if (check_value(ar, desired_ar, comparison_types["ar"]) and
                check_value(bpm, desired_bpm, comparison_types["bpm"]) and
                check_value(od, desired_od, comparison_types["od"]) and
                check_value(hp, desired_hp, comparison_types["hp"]) and
                check_value(length, desired_length, comparison_types["length"]) and
                check_value(cs, desired_cs, comparison_types["cs"]) and
                check_value(star, desired_star_rating, comparison_types["star"])):
                check_value(status, desired_status, comparison_types["status"])

                print(beatmap.get("id"))
                downloaded = helperlib.downloadosumap(beatmap.get("id"), artist, song_name)
                if downloaded:
                    i += downloaded
                break
