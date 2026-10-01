import os
from dotenv import load_dotenv
from tools import (
    search_song, play_movie, take_screenshot,
    search_brave, get_weather, open_website, open_app,
    remember_note, read_notes, delete_note,
    monitor_system, get_datetime, get_news
)

load_dotenv()

news_key = os.environ.get("NEWS_API_KEY")
NEWS_COUNT = 5

# Every handler returns either:
#   "text"                -> shown and spoken as-is
#   (display, speech)     -> full text for the screen, shorter text for voice


def _arg(command):
    return command.split(":", 1)[1].strip()


def handle_monitor_system(command):
    info = monitor_system()

    if info["battery_percent"] is not None:
        state = "Charging" if info["charging"] else "Not Charging"
        battery = f"{info['battery_percent']}% {state}"
    else:
        battery = "No Battery"

    text = (
        "Monitoring System Info, Sir...\n"
        f"CPU: {info['cpu_percent']}%\n"
        f"RAM: {info['ram_percent']}%\n"
        f"Battery: {battery}\n"
        f"Disk Usage: {info['disk_usage_percent']}%"
    )
    return text


def handle_datetime(command):
    check = _arg(command)
    now = get_datetime()

    if check == "date":
        return now["date"]
    if check == "time":
        return now["time"]
    if check == "datetime":
        return f"{now['date']} | {now['time']}"
    return "I didn't understand that date or time request, Sir."


def handle_open_website(command):
    sitename = _arg(command)
    open_website(sitename)
    return f"Opening {sitename}, Sir."


def handle_open_app(command):
    appname = _arg(command)
    if open_app(appname):
        return f"Opening {appname}, Sir."
    return f"Could not find {appname}, Sir."


def handle_search_brave(command):
    query = _arg(command)
    search_brave(query)
    return f"Searching for {query}, Sir."


def handle_get_weather(command):
    return get_weather(_arg(command))


def handle_take_screenshot(command):
    filename = take_screenshot()
    return f"Screenshot taken, Sir. Saved as {filename}", "Screenshot taken, Sir."


def handle_remember_note(command):
    task = _arg(command)
    remember_note(task)
    return f"{task}, added to your notes, Sir."


def handle_read_notes(command):
    notes = read_notes()
    if not notes:
        return "You have no notes, Sir."

    display = "NOTES.\n" + "\n".join(f"{i}. {note}" for i, note in enumerate(notes, 1))
    return display, "Here are your notes, Sir."


def handle_delete_note(command):
    note = _arg(command).lower()
    code = delete_note(note)

    if code == "ALL":
        return "All notes cleared, Sir."
    if code == "NoNotes":
        return "You have no notes, Sir."
    if code == "InvalidNoteNumber":
        return f"{note} is an invalid note number, Sir."
    return f"Deleted note: {code}"


def handle_play_movie(command):
    movie = _arg(command)
    if play_movie(movie) is None:
        return f"Could not find the movie {movie}, Sir."
    return f"Playing Movie: {movie}, Sir."


def handle_search_song(command):
    song = _arg(command)
    search_song(song)
    return f"Searching for {song} on Spotify, Sir."


def handle_get_news(command):
    parts = command.split(":", 3)
    if len(parts) < 4:
        return "I couldn't understand that news request, Sir."
    _, endpoint, time_interval, filters = parts

    articles = get_news(endpoint, time_interval, filters, NEWS_COUNT, news_key)

    if articles == "error":
        return "Unable to fetch news, Sir."
    if articles == "noresults":
        return "No results found, Sir."

    lines = []
    titles = []
    for i, article in enumerate(articles, 1):
        title = article.get("title") or "Untitled"
        source = (article.get("source") or {}).get("name", "Unknown")
        lines.append(
            f"{i}. {title}\n"
            f"   Source    : {source}\n"
            f"   Published : {article.get('publishedAt')}\n"
            f"   Summary   : {article.get('description') or 'No summary'}\n"
            f"   Read more : {article.get('url')}"
        )
        titles.append(title.rsplit(" - ", 1)[0])  # drop the " - Source" suffix

    display = "Top Headlines.\n\n" + "\n\n".join(lines)
    speech = "Here are the top headlines, Sir. " + ". ".join(titles)
    return display, speech


TOOLS = {
    "MONITORSYSTEM:": handle_monitor_system,
    "DATETIME:": handle_datetime,
    "OPENWEBSITE:": handle_open_website,
    "OPENAPP:": handle_open_app,
    "SEARCHBRAVE:": handle_search_brave,
    "WEATHER:": handle_get_weather,
    "TAKESCREENSHOT:": handle_take_screenshot,
    "REMEMBERNOTE:": handle_remember_note,
    "READNOTES:": handle_read_notes,
    "DELETENOTE:": handle_delete_note,
    "PLAYMOVIE:": handle_play_movie,
    "PLAYSONG:": handle_search_song,
    "GETNEWS:": handle_get_news,
}


def check_tools(command):
    """Returns (is_tool, display, speech)."""
    command = command.strip()

    for prefix, handler in TOOLS.items():
        if command.startswith(prefix):
            try:
                result = handler(command)
            except Exception as error:
                return True, f"That tool failed, Sir.\n\n{error}", "That tool failed, Sir.", command

            if isinstance(result, str):
                display = speech = result
            else:
                display, speech = result

            return True, display, speech

    return False, None, None