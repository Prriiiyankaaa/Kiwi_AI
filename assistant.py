import openai
import os
import pywhatkit
import requests
import datetime
import pyautogui
import webbrowser


WEATHER_API_KEY = "YOUR_API_KEY"

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
    return f"Screenshot saved at {path}"

def run_Kiwi_ai(user_input):
    query = user_input.lower().strip()

    # Weather
    if "weather" in query or "temperature" in query:
        return get_weather()

    # Play music
    if "play" in query:
        song = query.replace("play", "").strip()
        if not song:
            return "Please tell me the song name."
        pywhatkit.playonyt(song)
        return f"Playing {song} on YouTube."

    # Screenshot
    if "screenshot" in query:
        return take_screenshot()

    # Time
    if "time" in query:
        return f"The time is {datetime.datetime.now().strftime('%I:%M %p')}."

    # Open site
    websites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "weather": "https://weather.com",
    }
    for site in websites:
        if f"open {site}" in query:
            webbrowser.open(websites[site])
            return f"Opening {site}..."

    # Open macOS apps
    apps = {
        "notes": "Notes",
        "safari": "Safari",
        "vs code": "Visual Studio Code",
    }
    for app in apps:
        if f"open {app}" in query:
            os.system(f"open -a \"{apps[app]}\"")
            return f"Opening {app}..."

    # GPT fallback
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
