import openai
import os
#import pywhatkit
import requests
import datetime
#import pyautogui
import webbrowser

openai.api_key = os.getenv("OPENAI_API_KEY")


WEATHER_API_KEY = "03a25ff1295417cbd61db71bc48262eb"

def get_location():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        res.raise_for_status()
        loc = res.json().get("loc")
        if loc:
            lat, lon = loc.split(",")
            return float(lat), float(lon)
    except:
        pass
    return None, None

def get_weather():
    lat, lon = get_location()
    if not lat or not lon:
        return "Couldn't detect your location."

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data["cod"] == 200:
            city = data["name"]
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"The current temperature in {city} is {temp}°C with {desc}."
    except:
        pass
    return "Unable to fetch weather data."

def take_screenshot():
    folder = os.path.join(os.getcwd(), "screenshots")
    os.makedirs(folder, exist_ok=True)
    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.join(folder, filename)
    pyautogui.screenshot().save(path)
    return f"Screenshot saved"

def run_Kiwi_ai(user_input):
    query = user_input.lower().strip()

    if "weather" in query or "temperature" in query:
        return get_weather()


    if "play" in query:
        song = query.replace("play", "").strip()
        if not song:
            return "Please tell me the song name."
        pywhatkit.playonyt(song)
        return f"Playing {song} on YouTube."


    if "screenshot" in query:
        return take_screenshot()


    if "time" in query:
        return f"The time is {datetime.datetime.now().strftime('%I:%M %p')}."


    websites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "weather": "https://weather.com",
        "facebook": "https://www.facebook.com",
        "wikipedia": "https://en.wikipedia.org/wiki/Main_Page",
        "instagram": "https://www.instagram.com",
        "twitter": "https://x.com/",
        "github": "https://github.com",
        "stack overflow": "https://stackoverflow.com/",
        "linkedin": "https://linkedin.com",
        "gmail": "https://mail.google.com/",
        "drive": "https://drive.google.com/",
        "meet": "https://meet.google.com/",
        "maps": "https://maps.google.co.in"
    }
    for site in websites:
        if f"open {site}" in query:
            webbrowser.open(websites[site])
            return f"Opening {site}..."

    apps = {
            "facetime": "/System/Applications/FaceTime.app",
            "whatsapp": "/Applications/WhatsApp.app",
            "safari": "/Applications/Safari.app",
            "chrome": "/Applications/Google Chrome.app",
            "notes": "/System/Applications/Notes.app",
            "spotify": "/Applications/Spotify.app",
            "vscode": "/Applications/Visual Studio Code.app",
            "calendar": "/System/Applications/Calendar.app",
            "terminal": "/System/Applications/Utilities/Terminal.app",
            "camera": "/System/Applications/Photo Booth.app",
            "Prime video": "/Applications/Prime Video.app",
            "photos": "/System/Applications/Photos.app",
            "mail": "/System/Applications/Mail.app",
            "maps": "/Applications/Maps.app",
            "reminders": "/System/Applications/Reminders.app",
            "settings": "/System/Applications/System Settings.app",
            "music": "/System/Applications/Music.app",
            "messages": "/System/Applications/Messages.app",
            "contacts": "/System/Applications/Contacts.app",
            "canva" : "/Applications/Canva.app",
            "photoshop": "/Applications/Adobe Photoshop 2022/Adobe Photoshop 2022.app",
            "premiere pro": "/Applications/Adobe Premiere Pro 2022/Adobe Premiere Pro 2022.app",
            "illustrator": "/Applications/Adobe Illustrator 2022/Adobe Illustrator.app",
            "after effects": "/Applications/Adobe After Effects 2022/Adobe After Effects 2022.app",
            "indesign": "/Applications/Adobe InDesign 2022/Adobe InDesign 2022.app",
            "acrobat": "/Applications/Adobe Acrobat DC/Adobe Acrobat.app",
            "davinci resolve": "/Applications/DaVinci Resolve/DaVinci Resolve.app",
            "blender": "/Applications/Blender.app",
            "figma": "/Applications/Figma.app",
            "discord": "/Applications/Discord.app",
            "zoom": "/Applications/zoom.us.app",
            "notion": "/Applications/Notion.app",
            "slack": "/Applications/Slack.app",
            "trello": "/Applications/Trello.app",
            "telegram": "/Applications/Telegram.app",
        }
    for app in apps:
        if f"open {app}" in query:
            os.system(f"open -a \"{apps[app]}\"")
            return f"Opening {app}..."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Kiwi, a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print("GPT Error:", e)
        return "Sorry, I couldn't connect to OpenAI."
