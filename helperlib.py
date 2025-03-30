import requests
import os
import win32com.client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

osu_cookie = ""

def sanitize_filename(filename): # same story as initcookie
    invalid_chars = r'\/:*?"<>|'
    translation_table = str.maketrans("", "", invalid_chars)
    return filename.translate(translation_table)

def initcookie(): # i did not wanna deal with this so AI helped
    options = Options()
    user_profile_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')

    options.add_argument(f"user-data-dir={user_profile_path}")
    options.add_argument("profile-directory=Default")
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-gpu")  # Helps prevent some headless issues
    options.add_argument("--window-size=1920,1080")  # Set a virtual window size

    driver = webdriver.Chrome(options=options)
    driver.get('https://osu.ppy.sh/beatmapsets/732772#osu/1546003')

    for cookie in driver.get_cookies():
        if cookie.get("name") == "osu_session":
            global osu_cookie
            osu_cookie = cookie.get("value")
            print("got cookie")

    driver.quit()
    
def get_osu_path():
    windowsuser = os.getlogin()
    osu_path = rf"C:\Users\{windowsuser}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\osu!.lnk"
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(osu_path)
    osu_real_path = shortcut.TargetPath
    osu_real_dir = os.path.dirname(osu_real_path)
    
    beatmap_directory_value = ""

    config_path = f"{osu_real_dir}/osu!.{windowsuser}.cfg"
    with open(config_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("BeatmapDirectory"):
                beatmap_directory_value = line.split('=', 1)[1].strip()
                break
    if os.path.isabs(beatmap_directory_value):
        return beatmap_directory_value
    else:
        return os.path.abspath(os.path.join(osu_real_dir, beatmap_directory_value))

def checkifmapalreadyexists(beatmapsetid, path):
    onlyfiles = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    
    for file in onlyfiles:
        if str(file).startswith(f"{beatmapsetid}"):
            return True      
    return False  

def downloadosumap(beatmapset_id, artist, songname):
    osu_path = get_osu_path()
    if checkifmapalreadyexists(beatmapset_id, osu_path):
        print("you already have this map")
        return
    headers = {
    "Referer" : f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}",
    "Cookie" : f"osu_session={osu_cookie}",
    }
    redirect_url = None
    response = requests.get(f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}/download",headers=headers, allow_redirects=False)
    if "Location" in response.headers:
        redirect_url = response.headers["Location"]
    else:
        print(f"No redirect found. Status: {response.status_code}")

    if not redirect_url:
        return -1
    osubeatmap = requests.get(redirect_url)
    
    safe_songname = sanitize_filename(songname)
    safe_artist = sanitize_filename(artist)
    filename = rf"{osu_path}/{beatmapset_id} {safe_artist} - {safe_songname}.osz"

    if osubeatmap.status_code == 200:
        with open(filename, "wb") as f:
            f.write(osubeatmap.content)
    else:
        print(f"Failed to download. Status: {osubeatmap.status_code}, Response: {osubeatmap.text}")

    return 1
