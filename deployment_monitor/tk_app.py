import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import json
import os
import queue
from pathlib import Path

from core.folder_monitor import FolderMonitor
from core.zip_processor import ZipProcessor
from core.validator import DeploymentValidator
from core.jira_extractor import JiraExtractor
from core.archiver import Archiver
from core.cycle_manager import CycleManager

class DeploymentMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Deployment Log Verification - Tkinter UI")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e2f")

        self.service_running = False
        self.log_queue = queue.Queue()
        self.last_status = None

        self._setup_styles()
        self._create_widgets()
        
        # Start queue polling
        self.root.after(100, self._poll_log_queue)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        self.bg_color = "#1e1e2f"
        self.card_bg = "#2b2d42"
        self.accent_color = "#667eea"
        self.text_color = "#ffffff"
        self.btn_bg = "#764ba2"

        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Inter", 10))
        style.configure("Header.TLabel", background=self.card_bg, foreground=self.accent_color, font=("Playfair Display", 14, "bold"))
        style.configure("Status.TLabel", background=self.bg_color, foreground="#f2994a", font=("Inter", 11, "bold"))
        
        style.configure("TButton", background=self.btn_bg, foreground="white", font=("Inter", 10, "bold"), borderwidth=0)
        style.map("TButton", background=[("active", "#667eea")])

    def _create_widgets(self):
        # Main Container
        main_frame = ttk.Frame(self.root, style="TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        title_lbl = tk.Label(main_frame, text="🔁 Deployment Log Automation", bg=self.bg_color, fg=self.accent_color, font=("Playfair Display", 24, "bold"))
        title_lbl.pack(pady=(0, 20))

        # --- Configuration Card ---
        config_card = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        config_card.pack(fill="x", pady=10)
        
        ttk.Label(config_card, text="📥 Configuration", style="Header.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

        # Incoming Path
        ttk.Label(config_card, text="Incoming Folder Path:", background=self.card_bg).grid(row=1, column=0, sticky="w")
        self.incoming_var = tk.StringVar(value=r"C:\Users\loges\Desktop\deployment_monitor\incoming")
        self.incoming_ent = tk.Entry(config_card, textvariable=self.incoming_var, bg="#1a1a2e", fg="white", insertbackground="white", borderwidth=0, font=("Inter", 10))
        self.incoming_ent.grid(row=1, column=1, sticky="ew", padx=10, ipady=5)
        ttk.Button(config_card, text="📂 Open", command=lambda: self._open_folder(self.incoming_var.get())).grid(row=1, column=2)

        # Base Path
        ttk.Label(config_card, text="Base Audit Path:", background=self.card_bg).grid(row=2, column=0, sticky="w", pady=10)
        self.base_var = tk.StringVar(value=r"C:\deployment_audit_test")
        self.base_ent = tk.Entry(config_card, textvariable=self.base_var, bg="#1a1a2e", fg="white", insertbackground="white", borderwidth=0, font=("Inter", 10))
        self.base_ent.grid(row=2, column=1, sticky="ew", padx=10, ipady=5)
        ttk.Button(config_card, text="📁 Open", command=lambda: self._open_folder(self.base_var.get())).grid(row=2, column=2)

        # Poll Interval
        ttk.Label(config_card, text="Poll Interval (s):", background=self.card_bg).grid(row=3, column=0, sticky="w")
        self.poll_var = tk.IntVar(value=30)
        self.poll_spn = tk.Spinbox(config_card, from_=5, to=300, textvariable=self.poll_var, bg="#1a1a2e", fg="white", buttonbackground="#2b2d42", borderwidth=0, font=("Inter", 10))
        self.poll_spn.grid(row=3, column=1, sticky="w", padx=10, ipady=3, ipadx=10)

        config_card.columnconfigure(1, weight=1)

        # --- Control & Status ---
        control_frame = ttk.Frame(main_frame, style="TFrame")
        control_frame.pack(fill="x", pady=20)

        self.start_btn = tk.Button(control_frame, text="▶ Start Service", bg="#10b981", fg="white", font=("Inter", 11, "bold"), bd=0, padx=20, pady=10, command=self.start_service)
        self.start_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = tk.Button(control_frame, text="⏹ Stop Service", bg="#ef4444", fg="white", font=("Inter", 11, "bold"), bd=0, padx=20, pady=10, command=self.stop_service)
        self.stop_btn.pack(side="left")

        self.status_lbl = ttk.Label(control_frame, text="Service Status: STOPPED", style="Status.TLabel")
        self.status_lbl.pack(side="right")

        # --- Deployment Status ---
        self.deploy_status_frame = ttk.Frame(main_frame, style="TFrame")
        self.deploy_status_frame.pack(fill="x", pady=5)
        self.deploy_status_lbl = tk.Label(self.deploy_status_frame, text="📊 Latest Status: No deployment processed", bg=self.bg_color, fg="#a0a0a0", font=("Inter", 12, "bold"))
        self.deploy_status_lbl.pack(anchor="w")

        # --- Logs ---
        ttk.Label(main_frame, text="📜 Live Logs:", style="TLabel").pack(anchor="w", pady=(10, 5))
        self.log_area = scrolledtext.ScrolledText(main_frame, bg="#0f0c29", fg="#e0e0e0", font=("Consolas", 10), borderwidth=0, highlightthickness=0)
        self.log_area.pack(fill="both", expand=True)

    def _open_folder(self, path):
        if Path(path).exists():
            os.startfile(path)
        else:
            messagebox.showerror("Error", f"Path does not exist: {path}")

    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")

    def _poll_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_area.insert(tk.END, msg + "\n")
                self.log_area.see(tk.END)
                
                # Check for status updates in log messages (simple integration)
                if "Status: PASS" in msg:
                    self.update_deploy_status("PASS")
                elif "Status: FAIL" in msg:
                    self.update_deploy_status("FAIL")
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_log_queue)

    def update_deploy_status(self, status):
        if status == "PASS":
            self.deploy_status_lbl.config(text="📊 Latest Status: Deployment PASSED ✅", fg="#10b981")
        else:
            self.deploy_status_lbl.config(text="📊 Latest Status: Deployment FAILED ❌", fg="#ef4444")

    def start_service(self):
        if self.service_running:
            return

        incoming_path = self.incoming_var.get()
        base_path = self.base_var.get()
        interval = self.poll_var.get()

        if not Path(incoming_path).exists() or not Path(base_path).exists():
            messagebox.showerror("Error", "Check path configuration.")
            return

        self.service_running = True
        self.status_lbl.config(text="Service Status: RUNNING", foreground="#10b981")
        self.start_btn.config(state="disabled")
        
        self.thread = threading.Thread(target=self.run_service_task, args=(incoming_path, base_path, interval), daemon=True)
        self.thread.start()

    def stop_service(self):
        self.service_running = False
        self.status_lbl.config(text="Service Status: STOPPED", foreground="#f2994a")
        self.start_btn.config(state="normal")
        self.add_log("🛑 Stopping service...")

    def run_service_task(self, incoming_path_str, base_path_str, interval):
        incoming_path = Path(incoming_path_str)
        base_audit_path = Path(base_path_str)
        config_path = Path("config.json")

        if not config_path.exists():
            self.add_log("❌ config.json not found.")
            return

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        cycle_manager = CycleManager(base_audit_path)
        cycle_name = cycle_manager.generate_cycle_name()
        cycle_manager.ensure_cycle_folder(cycle_name)

        archiver = Archiver(base_audit_path, cycle_name)
        
        # Using Polling Folder Monitor
        monitor = FolderMonitor(incoming_path, poll_interval=interval)

        self.add_log(f"✅ Service Started (Polling Method). {cycle_name}")

        try:
            for file in monitor.start_polling():
                if not self.service_running:
                    break

                try:
                    self.add_log(f"Detected file: {file.name}")
                    zip_files = []
                    if file.suffix.lower() == ".msg":
                        from core.msg_processor import MsgProcessor
                        self.add_log("Extracting ZIP from MSG...")
                        msg_p = MsgProcessor(file, incoming_path)
                        zip_files.extend(msg_p.extract_zip_attachments())
                    elif file.suffix.lower() == ".zip":
                        zip_files.append(file)

                    for zip_path in zip_files:
                        self.add_log(f"Processing ZIP: {zip_path.name}")
                        zip_p = ZipProcessor(zip_path, config)
                        meta = zip_p.process()

                        validator = DeploymentValidator(meta, config)
                        result = validator.validate_all()

                        status = result["status"]
                        self.add_log(f"Status: {status}")
                        self.add_log(f"Details: {result['message']}")
                        
                        # Display detailed error information
                        if result.get("error_details"):
                            self.add_log("━ Error Details ━")
                            for error in result["error_details"]:
                                self.add_log(f"  • File: {error['file']} | Code: {error['code']}")
                                self.add_log(f"    Message: {error['message'][:100]}...")

                        jira_extractor = JiraExtractor(meta["main_log_path"])
                        jira_units = jira_extractor.extract()

                        archiver.archive(
                            status=status,
                            cluster=meta["cluster"],
                            instance=meta["instance"],
                            original_zip_path=zip_path,
                            jira_units=jira_units
                        )
                        zip_p.cleanup()

                    monitor.mark_as_processed(file)
                except Exception as e:
                    self.add_log(f"❌ Error processing {file.name}: {str(e)}")
        finally:
            self.add_log("🛑 Service Stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DeploymentMonitorApp(root)
    root.mainloop()
