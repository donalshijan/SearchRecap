# Search Recap — Frontend

This is the **frontend** for the Search Recap desktop app.  
It’s a lightweight, static web interface launched and can be viewed on the default browser on a new tab that, interacts with the FastAPI backend — providing a clean UI for viewing the dashboard for analytics, the flashcards of classified queries and generated summaries.

---

## 🧱 Overview

- Framework: **Vite + Node.js**
- Purpose:
  - Provide an interactive interface for users.
  - Communicate with the backend’s REST API endpoints.
  - Run as a standalone local server (via Node executable or `npm`).

---

## 🧪 Development Mode

To run the frontend for debugging or dev:

```bash
cd Frontend
npm install
npm run dev
```

By default, Vite serves the app at:

http://localhost:5173

### 🧩 Manual Test (without Launcher)

You can also start the frontend manually (after building):
```bash
cd Frontend
npm install
npm run build
node serve-with-node.cjs
```
This will find an available port starting from 5173 and will start serving the frontend app at that port on machine's Ip and localhost, will even open up that url on a new tab on the default browser.

Closed the tab accidentally? You can always click open on browser the url mentioned in the logs where it says it " Launching server at ip:port ", or copy paste on new browser tab.

Alternatively open up a new terminal and run
```bash
curl -X POST http://127.0.0.1:4000/open-browser
```
As you can probably tell, this means that serve-with-node.cjs also starts an http server at localhost:4000 where it has setup an 'open-browser' endpoint , which upon recieving a post request will open up a new tab in the default browser visiting the url where frontend is being served.

This choice of setting up a server for control purposes (like instructing reopen on browser tab) really comes in handy to conviniently setup an Inter Process Communication which works across all OS platforms especially given the fact that the launcher and the frontend are two separate processes written in two separate langauages and requiring different runtimes, and the latency of this method is totaly tolerable for the purposes. 
Therefore something like this would make it really easy to do stuff like, when we would want to have the same ' reopen frontend app on browser tab' kind of functionality on the launcher app, where with just a click of a button we can send this curl request at that endpoint and it opens up the app on a new tab.

## 🧱 Building the Frontend Executable

We use pkg to turn the frontend’s Node server into a standalone executable. So install pkg if not by running.
```bash
npm instal -g pkg
```
Go to project Root folder and
```bash
npm install
npm run build:frontend
```

This command builds the frontend static files via Vite.

Packages serve-with-node.cjs into platform-specific binaries.

The built executables appear under:

Frontend_builds/
├── frontend_main-win-x64.exe
├── frontend_main-linux-x64
└── frontend_main-macos-arm64


Move the relevant one to the project root.

🧩 Notes

You can also change the port number in serve-with-node.cjs if needed.

The launcher automatically starts this binary and opens it in your browser.

The frontend binary serves static content locally — no external network calls.

Make sure the backend is running before opening the frontend manually.

MIT License © 2025 Donal Shijan