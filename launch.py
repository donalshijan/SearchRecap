import os
import sys
import json
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import signal
import platform
import time
import requests
from typing import Any, Dict
import re


CONFIG_FILE = os.path.expanduser("~/.search_recap_config4.json")

class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Search Recap")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e1e")

        # Internal state
        self.backend_proc = None
        self.frontend_proc = None
        self.config = self.load_config()
        
        # Build UI
        self.build_ui()
        
        self._update_buttons_state(running=False)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        # handle termination signals (so Ctrl-C in terminal also shuts children)
        signal.signal(signal.SIGINT, lambda *_: self._on_closing())
        signal.signal(signal.SIGTERM, lambda *_: self._on_closing())

    # ----------------------------
    # CONFIG HANDLING
    # ----------------------------
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {
            "api_key": "",
            "activity_path": "",
            "model_name": "gpt-5-nano-2025-08-07",
            "database_path": ""
        }

    def save_config(self):
        # Clear old config if it exists
        if os.path.exists(CONFIG_FILE):
            try:
                os.remove(CONFIG_FILE)
            except Exception as e:
                print(f"⚠️ Failed to remove old config: {e}")

        # Write fresh config
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "api_key": self.api_key_var.get().strip(),
                "activity_path": self.activity_path_var.get().strip(),
                "model_name": self.model_name_var.get().strip(),
                "database_path": self.db_path_var.get().strip(),
            }, f, indent=2)
        print(f"✅ Config saved to {CONFIG_FILE}")

    # ----------------------------
    # UI SETUP
    # ----------------------------
    def build_ui(self):
        frame_top = tk.Frame(self.root, bg="#1e1e1e")
        frame_top.pack(pady=10, padx=10, fill="x")

        tk.Label(frame_top, text="OpenAI API Key:", fg="white", bg="#1e1e1e").grid(row=0, column=0, sticky="w")
        self.api_key_var = tk.StringVar(value=self.config.get("api_key", ""))
        tk.Entry(frame_top, textvariable=self.api_key_var, width=50, show="*").grid(row=0, column=1, padx=5)
        
        # Model Name
        tk.Label(frame_top, text="Model Name:", fg="white", bg="#1e1e1e").grid(row=1, column=0, sticky="w")
        self.model_name_var = tk.StringVar(value=self.config.get("model_name", "gpt-5-nano-2025-08-07"))
        tk.Entry(frame_top, textvariable=self.model_name_var, width=50).grid(row=1, column=1, padx=5)

        tk.Label(frame_top, text="MyActivity.json Path:", fg="white", bg="#1e1e1e").grid(row=2, column=0, sticky="w")
        self.activity_path_var = tk.StringVar(value=self.config.get("activity_path", ""))
        tk.Entry(frame_top, textvariable=self.activity_path_var, width=50).grid(row=2, column=1, padx=5)
        tk.Button(frame_top, text="Browse", command=self.browse_file, bg="#333", fg="black").grid(row=2, column=2, padx=5)
        
        # Database URL (optional)
        tk.Label(frame_top, text="Database File Path:", fg="white", bg="#1e1e1e").grid(row=3, column=0, sticky="w")
        # Load previously saved value (plain path only)
        db_path_value = self.config.get("database_path", "")
        self.db_path_var = tk.StringVar(value=db_path_value)
        tk.Entry(frame_top, textvariable=self.db_path_var, width=50).grid(row=3, column=1, padx=5)

        # Create a separate frame for action buttons below all input fields
        frame_actions = tk.Frame(frame_top, bg="#1e1e1e")
        frame_actions.grid(row=4, column=0, columnspan=4, pady=10)
        
        self.start_btn = tk.Button(frame_actions, text="Start App", command=self.start_app, bg="#4caf50", fg="black", width=15)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(frame_actions, text="Stop App", command=self.stop_app, bg="#f44336", fg="black", width=15)
        self.stop_btn.pack(side="left", padx=5)
        
        self.force_kill_btn = tk.Button(frame_actions, text="Force Kill", command=self.stop_app, bg="#f44336", fg="black", width=15)
        self.force_kill_btn.pack(side="left", padx=5)
        
        self.reopen_btn = tk.Button(frame_actions, text="Reopen Frontend", command=self.reopen_frontend, bg="#0078D7", fg="black", width=16)
        self.reopen_btn.pack(side="left", padx=8)
        
        # Log Panels
        frame_logs = tk.Frame(self.root, bg="#1e1e1e")
        frame_logs.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame_logs, text="Backend Logs", fg="white", bg="#1e1e1e").pack(anchor="w")
        self.backend_log = scrolledtext.ScrolledText(frame_logs, height=12, bg="#111", fg="#0f0", wrap="word")
        self.backend_log.pack(fill="both", expand=True, pady=5)

        tk.Label(frame_logs, text="Frontend Logs", fg="white", bg="#1e1e1e").pack(anchor="w")
        self.frontend_log = scrolledtext.ScrolledText(frame_logs, height=12, bg="#111", fg="#0ff", wrap="word")
        self.frontend_log.pack(fill="both", expand=True, pady=5)
        


    # ----------------------------
    # FILE DIALOG
    # ----------------------------
    def browse_file(self):
        path = filedialog.askopenfilename(title="Select myActivity.json", filetypes=[("JSON Files", "*.json")])
        if path:
            self.activity_path_var.set(path)
            
    def _proc_creation_args(self) -> dict[str, object]:
        """
        Return platform-appropriate kwargs to create a new process group so
        we can signal the group later.
        """
        if os.name == "nt":
            # On Windows: CREATE_NEW_PROCESS_GROUP so we can send CTRL_BREAK_EVENT
            return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        else:
            # On Unix: start a new session (process group)
            return {"preexec_fn": os.setsid}

    def _terminate_proc_gracefully(self, proc, name="process", timeout=5.0):
        """Try graceful shutdown, else force-kill. Returns True if terminated."""
        if not proc or proc.poll() is not None:
            return True

        try:
            if os.name == "nt":
                # Send CTRL_BREAK_EVENT to the process group
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(proc.pid, signal.SIGINT)
        except Exception as e:
            # If sending signal fails, try proc.terminate()
            try:
                proc.terminate()
            except Exception:
                pass

        # wait up to timeout seconds
        try:
            proc.wait(timeout=timeout)
            return True
        except subprocess.TimeoutExpired:
            # still alive -> force kill
            try:
                if os.name == "nt":
                    proc.kill()
                else:
                    os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                pass
            try:
                proc.wait(timeout=2)
            except Exception:
                pass
            return False

    def _update_buttons_state(self, running: bool):
        """Enable/disable buttons depending on whether app is running."""
        # Find widgets by attribute (we assume you keep references)
        try:
            self.start_btn.config(state="disabled" if running else "normal")
            self.stop_btn.config(state="normal" if running else "disabled")
            self.force_kill_btn.config(state="normal" if running else "disabled")
            self.reopen_btn.config(state="normal" if running else "disabled")
        except Exception:
            pass

    # ----------------------------
    # APP START/STOP
    # ----------------------------
    def wait_for_backend_ready(self, process, timeout=40):
        """Wait for backend stdout to confirm startup or timeout."""
        start_time = time.time()
        ready = False
        buffer = ""
        while time.time() - start_time < timeout:
            line = process.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            buffer += line
            self.backend_log.insert(tk.END, line)
            self.backend_log.see(tk.END)

            if "Application startup complete" in line or "Backend running" in line:
                ready = True
                self.backend_log.insert(tk.END, "✅ Backend confirmed running!\n")
                self.backend_log.see(tk.END)
                break

        if not ready:
            self.backend_log.insert(tk.END, "❌ Backend failed to start in time.\n")
            self._terminate_proc_gracefully(process, "backend")
            raise TimeoutError("Backend did not signal readiness within timeout.")
        
    def _frontend_log_watcher(self, line) -> bool : 
        """Watch frontend logs for control server endpoint."""
        
        match = re.search(r"🎮 Control server listening on port (http[s]?://[^\s]+)", line)
        if match:
            self.control_endpoint = match.group(1)
            self.frontend_log.insert(
                tk.END,
                f"🎯 Detected control endpoint: {self.control_endpoint}\n"
            )
            self.frontend_log.see(tk.END)
            return True
        return False
    
    def start_app(self):
        
        if self.backend_proc and self.backend_proc.poll() is None:
            messagebox.showinfo("Backend server Already running")
            return
        
        if self.frontend_proc and self.frontend_proc.poll() is None:
            messagebox.showinfo("Frontend server Already running")
            return
        
        api_key = self.api_key_var.get().strip()
        activity_path = self.activity_path_var.get().strip()

        if not api_key:
            messagebox.showerror("Missing Field", "Please enter your OpenAI API key before starting.")
            return
        if not activity_path:
            messagebox.showerror("Missing Field", "Please select your myActivity.json file before starting.")
            return
        if not os.path.exists(activity_path):
            messagebox.showerror("Invalid File", f"The selected myActivity.json file does not exist:\n{activity_path}")
            return
        
        self.save_config()
        self.write_env_file()

        # Example executables (these should be your built binaries)
        backend_exec = os.path.join(os.getcwd(), "backend_main.exe" if os.name == "nt" else "./backend_main")
        frontend_exec = None
        if os.name == "nt":
            frontend_exec = os.path.join(os.getcwd(), "frontend_main-win-x64.exe")
        elif sys.platform == "darwin":
            frontend_exec = os.path.join(os.getcwd(), "frontend_main-macos-arm64")
        elif sys.platform.startswith("linux"):
            frontend_exec = os.path.join(os.getcwd(), "frontend_main-linux-x64")
        else:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")
        
        if not os.path.exists(backend_exec):
            messagebox.showerror("Error", f"Backend executable not found: {backend_exec}")
            return
        if not os.path.exists(frontend_exec):
            messagebox.showerror("Error", f"Frontend executable not found: {frontend_exec}")
            return

        # Launch backend
        create_kwargs: dict[str, object] = self._proc_creation_args()
        try:
            
            self.backend_proc = subprocess.Popen(
                [backend_exec],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                **create_kwargs # type: ignore[arg-type]
            )
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to start backend: {e}")
            return
        
        threading.Thread(target=self.stream_output, args=(self.backend_proc, self.backend_log), daemon=True).start()
        
        # Wait for backend to be ready before frontend launch
        try:
            self.wait_for_backend_ready(self.backend_proc)
        except Exception as e:
            messagebox.showerror("Backend Startup Failed", str(e))
            return

        # Launch frontend
        try:
            self.frontend_proc = subprocess.Popen(
                [frontend_exec],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                **create_kwargs # type: ignore[arg-type]
            )
        except Exception as e:
            # If frontend fails, try to stop backend
            messagebox.showerror("Launch Error", f"Failed to start frontend: {e}")
            self._terminate_proc_gracefully(self.backend_proc, "backend")
            self.backend_proc = None
            return
        
        threading.Thread(target=self.stream_output, args=(self.frontend_proc, self.frontend_log , self._frontend_log_watcher ), daemon=True).start()

        self.backend_log.insert(tk.END, "Backend started...\n")
        self.frontend_log.insert(tk.END, "Frontend started...\n")
        
         # Disable start, enable stop buttons
        self._update_buttons_state(running=True)

    def stop_app(self):
        if not any([self.backend_proc, self.frontend_proc]):
            messagebox.showinfo("Nothing to stop", "No processes are currently running.")
            return
        
        # Attempt graceful termination
        if self.backend_proc and self.backend_proc.poll() is None:
            self.backend_log.insert(tk.END, "Gracefully stopping backend...\n")
            self._terminate_proc_gracefully(self.backend_proc, "backend", timeout=5.0)
        if self.frontend_proc and self.frontend_proc.poll() is None:
            self.frontend_log.insert(tk.END, "Gracefully stopping frontend...\n")
            self._terminate_proc_gracefully(self.frontend_proc, "frontend", timeout=5.0)
            
        self.backend_proc = None
        self.frontend_proc = None
            
        self.backend_log.insert(tk.END, "Stopped all processes.\n")
            
            # Re-enable start button
        self._update_buttons_state(running=False)
    
    def force_kill_app(self):
        if not any([self.backend_proc, self.frontend_proc]):
            messagebox.showinfo("Nothing to kill", "No processes are currently running.")
            
        for proc, widget_log in ((self.backend_proc, self.backend_log), (self.frontend_proc, self.frontend_log)):
            if proc and proc.poll() is None:
                try:
                    widget_log.insert(tk.END, "Force killing process...\n")
                    if os.name == "nt":
                        proc.kill()
                    else:
                        os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait(timeout=2)
                except Exception as e:
                    widget_log.insert(tk.END, f"Force kill error: {e}\n")
        
        self.backend_proc = None
        self.frontend_proc = None
        
        self.backend_log.insert(tk.END, "💀 Force killed all processes.\n")
        # Re-enable start button
        self._update_buttons_state(running=False)
        
    def _on_closing(self):
        # Attempt to stop children gracefully before quitting
        try:
            if any([self.backend_proc, self.frontend_proc]):
                self.stop_app()
        except Exception:
            pass
        # give a moment for children to exit
        time.sleep(0.2)
        try:
            self.root.destroy()
        except Exception:
            os._exit(0)

    # ----------------------------
    # STREAM OUTPUT TO UI
    # ----------------------------
    def stream_output1(self, process, text_widget):
        for line in iter(process.stdout.readline, ''):
            text_widget.insert(tk.END, line)
            text_widget.see(tk.END)
        process.stdout.close()
    
    def stream_output(self, process, text_widget, line_callback=None):
        """
        Stream logs from a process into a Tkinter text widget.
        Optionally run a callback(line) on each line (e.g., for pattern matching).
        """
        for line in iter(process.stdout.readline, ''):
            text_widget.insert(tk.END, line)
            text_widget.see(tk.END)

            if line_callback:
                try:
                    stop_callback = line_callback(line)
                    if(stop_callback): line_callback=None
                except Exception as e:
                    text_widget.insert(tk.END, f"⚠️ Log callback error: {e}\n")

        process.stdout.close()
            
    def write_env_file(self):
        env_path = os.path.join(os.getcwd(), ".env")

        # Clear old .env if it exists
        if os.path.exists(env_path):
            try:
                os.remove(env_path)
            except Exception as e:
                print(f"⚠️ Failed to remove old .env: {e}")

        # Write fresh .env file
        env_content = (
        f"OPENAI_API_KEY={self.api_key_var.get().strip()}\n"
        f"MODEL_NAME={self.model_name_var.get().strip()}\n"
        f"MYACTIVITY_JSON_FILE={self.activity_path_var.get().strip()}\n"
        f"DATABASE_URL=sqlite:///{self.db_path_var.get().strip()}\n"
        )
        try:
            with open(env_path, "w") as f:
                f.write(env_content)
            print(f"✅ .env file created at {env_path}")
        except Exception as e:
            messagebox.showerror("Error Writing .env", f"Failed to write .env:\n{e}")
            
    def reopen_frontend(self):
        """Try to reopen the frontend in a browser via its control endpoint."""
        FRONTEND_CONTROL_ENDPOINT = "http://127.0.0.1:4000/open-browser"
        endpoint = getattr(self, "control_endpoint", None)
        if not endpoint:
            self.frontend_log.insert(tk.END, "⚠️ Control endpoint not yet known. Try restarting frontend.\n")
            return
        try:
            resp = requests.post(endpoint, timeout=2)
            if resp.status_code == 200:
                self.frontend_log.insert(tk.END, "✅ Reopened frontend in browser.\n")
            else:
                self.frontend_log.insert(
                    tk.END, f"⚠️ Frontend responded with status {resp.status_code}.\n"
                )
        except requests.exceptions.ConnectionError:
            self.frontend_log.insert(
                tk.END,
                "❌ Could not connect to frontend control endpoint — "
                "is the frontend running?\n",
            )
        except Exception as e:
            self.frontend_log.insert(tk.END, f"❌ Unexpected error while reopening: {e}\n")

            
# ----------------------------
# MAIN ENTRY
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AppLauncher(root)
    root.mainloop()
