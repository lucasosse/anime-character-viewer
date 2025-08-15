```markdown
# 🎌 Anime Search

A lightweight desktop application for searching anime information—packaged as a standalone `.exe` using PyInstaller. No terminal window, just a clean user experience.

---

## 📦 Features

- 🔍 Search for anime titles quickly
- 🖼️ GUI-based interface (no command line required)
- 📁 Packaged into a single `.exe` file for easy distribution
- 🚫 No console window on launch

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/anime-search.git
cd anime-search
```

### 2. Install Dependencies

Make sure you have Python 3.7+ installed. Then run:

```bash
pip install -r requirements.txt
```

> If you don't have a `requirements.txt`, you can manually install any needed libraries like `tkinter`, `requests`, or `PyQt5` depending on your GUI framework.

---

## 🛠️ Build the Executable

Use PyInstaller to package the script:

```bash
pyinstaller --onefile --noconsole anime-search.py
```

The executable will be located in the `dist/` folder:

```
dist/anime-search.exe
```

---

## 📁 Project Structure

```
anime-search/
├── anime-search.py
├── README.md
├── requirements.txt
└── dist/
    └── anime-search.exe
```

---

## 🧊 Optional: Add an Icon

To add a custom icon to your executable:

```bash
pyinstaller --onefile --noconsole --icon=icon.ico anime-search.py
```

Make sure `icon.ico` is in the same directory.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

