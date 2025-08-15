import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import re

# Windows-only clipboard support
try:
    import win32clipboard
except ImportError:
    win32clipboard = None

# --- GraphQL Queries ---
SEARCH_ANIME_QUERY = """
query ($search: String) {
  Page(perPage: 10) {
    media(search: $search, type: ANIME) {
      id
      title {
        romaji
      }
    }
  }
}
"""

CHARACTER_QUERY = """
query ($id: Int) {
  Media(id: $id, type: ANIME) {
    characters(perPage: 25) {
      edges {
        node {
          name {
            full
            first
            last
          }
          image {
            large
          }
        }
      }
    }
  }
}
"""

SEARCH_CHARACTER_QUERY = """
query ($search: String) {
  Page(perPage: 10) {
    characters(search: $search) {
      id
      name {
        full
        first
        last
      }
      image {
        large
      }
      media {
        nodes {
          title {
            romaji
          }
        }
      }
    }
  }
}
"""

# --- Helper Functions ---
def is_japanese(text):
    return bool(re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text))

def search_anime_list(anime_name):
    url = "https://graphql.anilist.co"
    variables = {"search": anime_name}
    response = requests.post(url, json={"query": SEARCH_ANIME_QUERY, "variables": variables})
    data = response.json()
    return data["data"]["Page"]["media"]

def get_characters(anime_id):
    url = "https://graphql.anilist.co"
    variables = {"id": anime_id}
    response = requests.post(url, json={"query": CHARACTER_QUERY, "variables": variables})
    data = response.json()
    return data["data"]["Media"]["characters"]["edges"]

def search_character_list(character_name):
    url = "https://graphql.anilist.co"
    variables = {"search": character_name}
    response = requests.post(url, json={"query": SEARCH_CHARACTER_QUERY, "variables": variables})
    data = response.json()
    return data["data"]["Page"]["characters"]

def show_character_image(image_url):
    response = requests.get(image_url)
    img_data = response.content
    img = Image.open(BytesIO(img_data)).resize((200, 300))
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo

# --- GUI Functions ---
def fetch_anime_list():
    anime_name = anime_entry.get()
    results = search_anime_list(anime_name)
    anime_dropdown["values"] = []
    if results:
        global anime_results
        anime_results = results
        titles = [anime["title"]["romaji"] for anime in anime_results]
        anime_dropdown["values"] = titles
        anime_dropdown.current(0)
        status_label.config(text=f"Found {len(titles)} anime results.")
    else:
        status_label.config(text="No anime found.")

def fetch_characters_from_selected():
    selected_index = anime_dropdown.current()
    if selected_index < 0 or selected_index >= len(anime_results):
        status_label.config(text="Please select an anime.")
        return

    anime_id = anime_results[selected_index]["id"]
    global characters
    characters = get_characters(anime_id)
    character_listbox.delete(0, tk.END)
    for char in characters:
        character_listbox.insert(tk.END, char["node"]["name"]["full"])
    status_label.config(text=f"Found {len(characters)} characters.")

def fetch_character_list():
    name = character_entry.get()
    results = search_character_list(name)
    character_dropdown["values"] = []
    if results:
        global character_results
        character_results = results
        names = [char["name"]["full"] for char in character_results]
        character_dropdown["values"] = names
        character_dropdown.current(0)
        status_label.config(text=f"Found {len(names)} character results.")
    else:
        status_label.config(text="No characters found.")

def show_selected_character():
    selected_index = character_dropdown.current()
    if selected_index < 0 or selected_index >= len(character_results):
        status_label.config(text="Please select a character.")
        return

    char = character_results[selected_index]
    first = char["name"].get("first", "")
    last = char["name"].get("last", "")
    if first and last:
        if is_japanese(last):
            formatted_name = f"{last} {first}"
        else:
            formatted_name = f"{first} {last}"
    else:
        formatted_name = char["name"]["full"]

    anime_titles = [media["title"]["romaji"] for media in char["media"]["nodes"]]
    anime_info = ", ".join(anime_titles) if anime_titles else "Unknown anime"

    name_label.config(text=f"{formatted_name} — {anime_info}")
    show_character_image(char["image"]["large"])

    global last_image_url
    last_image_url = char["image"]["large"]

def on_character_select(event):
    selected_index = character_listbox.curselection()
    if selected_index:
        idx = selected_index[0]
        char = characters[idx]["node"]
        image_url = char["image"]["large"]

        first = char["name"].get("first", "")
        last = char["name"].get("last", "")
        if first and last:
            if is_japanese(last):
                formatted_name = f"{last} {first}"
            else:
                formatted_name = f"{first} {last}"
        else:
            formatted_name = char["name"]["full"]

        name_label.config(text=f"{formatted_name}")
        show_character_image(image_url)

        global last_image_url
        last_image_url = image_url

def copy_name_to_clipboard():
    name = name_label.cget("text")
    root.clipboard_clear()
    root.clipboard_append(name)

def copy_image_to_clipboard():
    if not last_image_url or not win32clipboard:
        status_label.config(text="Image copy not supported on this platform.")
        return

    response = requests.get(last_image_url)
    img = Image.open(BytesIO(response.content))

    output = BytesIO()
    img.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()
    status_label.config(text="Image copied to clipboard.")

# --- GUI Setup ---
root = tk.Tk()
root.title("Anime & Character Viewer (AniList)")

# Anime search
tk.Label(root, text="Search Anime:").pack()
anime_entry = tk.Entry(root, width=40)
anime_entry.pack()
tk.Button(root, text="Search Anime", command=fetch_anime_list).pack()
anime_dropdown = ttk.Combobox(root, state="readonly", width=50)
anime_dropdown.pack()
tk.Button(root, text="Fetch Characters", command=fetch_characters_from_selected).pack()

# Character list from anime
character_frame = tk.Frame(root)
character_frame.pack(side=tk.LEFT, fill=tk.Y)
character_scrollbar = tk.Scrollbar(character_frame)
character_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

character_listbox = tk.Listbox(character_frame, width=30, height=20, yscrollcommand=character_scrollbar.set)
character_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
character_scrollbar.config(command=character_listbox.yview)
character_listbox.bind("<<ListboxSelect>>", on_character_select)

# Character search
tk.Label(root, text="Search Character:").pack()
character_entry = tk.Entry(root, width=40)
character_entry.pack()
tk.Button(root, text="Search Character", command=fetch_character_list).pack()
character_dropdown = ttk.Combobox(root, state="readonly", width=50)
character_dropdown.pack()
tk.Button(root, text="Show Character", command=show_selected_character).pack()

# Image and name display
image_label = tk.Label(root)
image_label.pack(side=tk.RIGHT, padx=10)

name_label = tk.Label(root, text="Selected Character: ")
name_label.pack()

copy_name_btn = tk.Button(root, text="Copy Name", command=copy_name_to_clipboard)
copy_name_btn.pack()

copy_image_btn = tk.Button(root, text="Copy Image", command=copy_image_to_clipboard)
copy_image_btn.pack()

status_label = tk.Label(root, text="")
status_label.pack()

# Globals
last_image_url = None
characters = []
anime_results = []
character_results = []

root.mainloop()