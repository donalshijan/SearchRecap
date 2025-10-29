
# 🧠 Search Recap

### Your Personal Search History Summarizer — Powered by LLMs

**Search Recap** is a desktop application that takes your exported **Google MyActivity.json** file and uses an **AI backend** (OpenAI GPT-based model) to generate summaries, insights, and analytics about your search behavior over time — all wrapped in a simple local app that doesn’t send your data anywhere rather keeps in confined in your local machine.

The app bundles three main components:

1. **Backend (FastAPI)** — Processes your MyActivity data, interacts with the OpenAI API, and serves responses.
2. **Frontend (Static + Node wrapper)** — A minimal local web app for interaction and visualization.
3. **Tkinter Desktop Launcher** — The bridge that runs both backend and frontend executables, manages config (API keys, DB paths, etc.), and gives you live logs.

---

## 🚀 Features

* 🧩 **Fully local execution** — Nothing gets uploaded; all components run on your machine.
* 🔑 **OpenAI API integration** — Summarization, categorization, and insight generation.
* 💾 **SQLite/Database support** — Store and re-query processed data.
* 🧱 **Cross-platform executables** — Build and run application on Windows, macOS, or Linux, with frontend accessible on any device in the local home network, that can open up a browser.
* 🧍‍♂️ **Simple launcher UI** — Configure keys, paths, and start/stop the servers with one click.

---

## 🛠️ Directory Structure

```
GoogleSearchRecap/
│
├── Backend/                     # FastAPI source
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── Frontend/                    # Vite/React (or static) frontend
│   ├── dist/
│   ├── serve-with-node.cjs
│   ├── package.json
│   └── ...
│
├── launch.py                    # Tkinter launcher
├── backend_main / .exe          # Built backend binary
├── frontend_main-*              # Platform-specific frontend binaries
└── README.md
```

---

## 🧩 Requirements

* Python **3.10+**
* Node.js **v22.18.0+**
* npm or yarn
* OpenAI API key
* A downloaded **Google MyActivity.json** (from [Google Takeout](https://takeout.google.com))

---
### 💽  Building the backend and frontend executables
## 🏗️ Build Steps

### 1. 🧱 Backend Build (via PyInstaller)

🧰 Prerequisites

Make sure you have Python 3.10+ installed and venv available.

🌀 Create and Activate Virtual Environment

From your project root directory:

```bash
python3 -m venv .venv
```

Activate the environment:

macOS/Linux:
```bash
source .venv/bin/activate
```

Windows (CMD):
```bash
.venv\Scripts\activate
```

Once activated, your terminal prompt should look like:
```bash
(.venv) ➜ SearchRecap
```
Install backend dependencies
```bash
cd Backend
pip3 install -r requirements.txt
cd ..
```
From Project Root Directory:

Install pyinstaller if not already
```bash
pip3 install pyinstaller
```

Build backend executable using pyinstaller
```bash
pyinstaller --onefile --name backend_main ./Backend/main.py --add-data ".env:."
```
This generates a single binary (backend_main.exe on Windows, or just backend_main on Unix) inside dist/.

The built binary (`backend_main` or `backend_main.exe`) will appear in `dist/`.
Move it to the root directory of the project.

---

### 2. 🧰 Frontend Build (via pkg)

Building frontend from project root
```bash
cd Frontend
npm install
npm run build
cd ..
npm install
npm run build:frontend
```

This generates platform-specific binaries inside `Frontend_builds/`:

```
frontend_main-win-x64.exe
frontend_main-macos-arm64
frontend_main-linux-x64
```

Move the appropriate binary to the project root.

---

### 3. ⚙️ Run the App (Tkinter Launcher)

Back in the root directory:

```bash
python3 launch.py
```

You’ll see the desktop UI where you can:

* Enter your OpenAI API key
* Choose your `MyActivity.json`
* Start/Stop the backend and frontend servers
* View logs in real time

---

## 🧪 Development Mode (no builds)

If you want to test without compiling binaries:

1. Run backend manually:

   ```bash
   python3 Backend.main
   ```
2. Serve frontend (for example, with Vite):

   ```bash
   cd Frontend
   npm run dev
   ```
3. To launch both backend and frontend from project root using launch script:

    ```bash
    node launch.js 
    ```
    This launches frontend app on dev server after waiting and confirming backend has launched successfully and gracefully exits upon timeout, Displays logs from both backend and frontend on same terminal window with different colored prefix.

4. Launch the Tkinter app from project Root folder:

   ```bash
   python3 launch.py
   ```

---

## 📦 Upcoming: Automated Build Script

We’re working on a unified build pipeline (`build_all.py`) that will:

* Build backend (PyInstaller)
* Build frontend (pkg)
* Move all executables to project root
* Package versioned releases for Windows/macOS/Linux automatically.

---

## ⚠️ Notes

* The `.env` file is auto-generated when launching via Tkinter.
* The SQLite database URL field auto-prefixes `sqlite:///` — you just type the file path.
* The app does **not** collect or transmit data. Everything runs locally.

---

## 📜 License

This repository is primarily licensed under the **MIT License** — see [LICENSE](./LICENSE).

However, some components may carry their own licenses:

- `inference_manager/` is licensed under the **Apache License 2.0**  
  (see [inference_manager/LICENSE](./inference_manager/LICENSE)).

By using this repository, you agree to comply with the terms of each applicable license.

## 💖 Support My Work

Found this useful?
Well, Code doesn’t pour itself — and neither does vodka.
If my work made your life a little easier, consider dropping a small donation to keep the spirits flowing 😉.

👉 [  Send a 🥃 shot on paypal ](https://paypal.me/donalshijan)