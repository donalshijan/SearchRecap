# 🧠 Search Recap — Backend

This is the **FastAPI backend** for the Search Recap desktop app.  
It’s responsible for loading your exported **Google MyActivity.json**, processing and storing it (optionally in SQLite), and generating summaries and insights using the **OpenAI API**.

---

## ⚙️ Overview

- Framework: **FastAPI** + **Uvicorn**
- Language: **Python 3.10+**
- Responsibilities:
  - Parse and filter Google MyActivity data.
  - Store data in SQLite (or another configured DB).
  - Interact with OpenAI’s API for summarization.
  - Expose endpoints for the frontend and launcher to communicate with.

---

## 🏃‍♂️ Run the Backend

Make sure you create and populate a .env file in project Root folder, by following the example provided in .env.example file.
To start the backend manually from project root folder during development:

```bash
python3 -m Backend.main
```

or equivalently:
```bash
uvicorn Backend.main:app --host 0.0.0.0 --port 8000 
```

This launches the FastAPI app on your local network.
You can verify it by visiting:

http://127.0.0.1:8000/docs


Or to test LAN accessibility, open the following on another device connected to the same network (replace with your machine’s IP):

http://192.168.x.x:8000/docs

🧩 API Docs

Once the server is running, the automatically generated interactive API documentation is available at:

http://localhost:8000/docs


You can test endpoints, inspect request/response models, and validate payloads right from there.

🧨 Stopping the Backend (when Ctrl+C doesn’t work)

Sometimes Uvicorn spawns stubborn child processes that won’t die gracefully — classic case of zombie processes.
If pressing Ctrl + C doesn’t stop the server, do this:

Find the process:
```bash
ps aux | grep uvicorn
```

Kill the rogue process:
```bash
kill -9 <pid>
```

Replace <pid> with the actual process ID listed in the output.

You can confirm it’s gone with:
```bash
ps aux | grep uvicorn
```

If nothing shows up except your grep command, you’re good to go.


🧱 Building Executable

To bundle this backend into a single distributable file for use by the launcher:
Go to project root folder and
```bash
pyinstaller --onefile --name backend_main ./Backend/main.py --add-data ".env;."
```

This produces:

dist/backend_main (or backend_main.exe on Windows)


Move it to the project root directory.

⚠️ Notes

Ensure your OpenAI API key is set in the environment or passed from the launcher.

The backend defaults to localhost:8000 unless overridden.

SQLite path and config values are written via .env or runtime args.

To serve other devices on your network, ensure the port (default 8000) is open on your firewall.

MIT License © 2025 Donal Shijan