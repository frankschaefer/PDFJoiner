"""CustomTkinter GUI for Batch PDF Processing."""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import time
import os
from pathlib import Path
from typing import List
from .batch_processor import BatchProcessor
from . import __version__, __release_date__, __author__


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class BatchPDFJoinerApp(ctk.CTk):
    """Main application window for Batch PDF Joiner."""

    def __init__(self):
        super().__init__()

        self.title(f"PDF Batch Joiner v{__version__}")
        self.geometry("900x700")

        self.base_path = "/Users/fs_mku/Desktop/January 5, 2026 08:38 PM"
        self.processor = BatchProcessor()
        self.processor.set_progress_callback(self._on_progress_update)
        self.processor.set_log_callback(self._on_log_message)

        self.selected_folders: List[str] = []
        self.start_time = None
        self.processing_thread = None

        self._setup_ui()
        self._load_folders()

    def _setup_ui(self):
        """Set up the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header Frame
        self._create_header()

        # Folder selection frame
        self._create_folder_selection()

        # Log frame
        self._create_log_frame()

        # Progress frame
        self._create_progress_frame()

        # Control buttons
        self._create_control_buttons()

        # Status bar
        self._create_status_bar()

    def _create_header(self):
        """Create header with title and version info."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="PDF Batch Joiner",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        version_label = ctk.CTkLabel(
            header_frame,
            text=f"Version {__version__} | Released {__release_date__}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        version_label.grid(row=1, column=0, sticky="w")

    def _create_folder_selection(self):
        """Create folder selection area."""
        folder_frame = ctk.CTkFrame(self)
        folder_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        folder_frame.grid_columnconfigure(0, weight=1)
        folder_frame.grid_rowconfigure(3, weight=1)

        # Title and browse button row
        title_row = ctk.CTkFrame(folder_frame, fg_color="transparent")
        title_row.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_row,
            text="Select Folders to Process:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        # Browse button
        self.browse_button = ctk.CTkButton(
            title_row,
            text="📁 Select Start Folder",
            command=self._browse_folder,
            width=180,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8"
        )
        self.browse_button.grid(row=0, column=1, padx=(10, 0))

        # Base path label
        self.path_label = ctk.CTkLabel(
            folder_frame,
            text=f"Base: {self.base_path}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.path_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        # Status label for folder count
        self.folder_count_label = ctk.CTkLabel(
            folder_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.folder_count_label.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")

        # Folder list (scrollable with checkboxes)
        self.folder_scroll = ctk.CTkScrollableFrame(folder_frame, height=150)
        self.folder_scroll.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.folder_scroll.grid_columnconfigure(0, weight=1)

        self.folder_checkboxes = {}

        # Delete source files option
        self.delete_source_var = ctk.BooleanVar(value=True)
        self.delete_checkbox = ctk.CTkCheckBox(
            folder_frame,
            text="Remove source files after successful merge (recommended)",
            variable=self.delete_source_var,
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        )
        self.delete_checkbox.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="w")

    def _create_log_frame(self):
        """Create log output frame."""
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            log_frame,
            text="Processing Log:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.log_text = ctk.CTkTextbox(log_frame, height=200)
        self.log_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def _create_progress_frame(self):
        """Create progress bar and status."""
        progress_frame = ctk.CTkFrame(self)
        progress_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)

        # Progress label
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to process",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)

    def _create_control_buttons(self):
        """Create control buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, padx=20, pady=10)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ Start Processing",
            command=self._start_processing,
            width=150,
            height=40,
            fg_color="green",
            hover_color="darkgreen",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = ctk.CTkButton(
            button_frame,
            text="⏸ Pause",
            command=self._pause_processing,
            width=150,
            height=40,
            state="disabled",
            font=ctk.CTkFont(size=14)
        )
        self.pause_button.grid(row=0, column=1, padx=5)

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹ Stop",
            command=self._stop_processing,
            width=150,
            height=40,
            state="disabled",
            fg_color="red",
            hover_color="darkred",
            font=ctk.CTkFont(size=14)
        )
        self.stop_button.grid(row=0, column=2, padx=5)

        self.quit_button = ctk.CTkButton(
            button_frame,
            text="✕ Exit Application",
            command=self._quit_application,
            width=150,
            height=40,
            fg_color="#6b7280",
            hover_color="#4b5563",
            font=ctk.CTkFont(size=14)
        )
        self.quit_button.grid(row=0, column=3, padx=5)

    def _create_status_bar(self):
        """Create status bar with time information."""
        status_frame = ctk.CTkFrame(self, height=30)
        status_frame.grid(row=5, column=0, padx=0, pady=0, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)

        self.time_label = ctk.CTkLabel(
            status_frame,
            text="Elapsed: 00:00:00 | Estimated: --:--:--",
            font=ctk.CTkFont(size=11)
        )
        self.time_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.author_label = ctk.CTkLabel(
            status_frame,
            text=f"© {__author__}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.author_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")

    def _browse_folder(self):
        """Open folder browser to select base directory."""
        # Get initial directory - use parent of current base_path if it exists
        initial_dir = self.base_path
        if not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~/Desktop")

        folder_selected = filedialog.askdirectory(
            title="Select Base Folder",
            initialdir=initial_dir
        )

        if folder_selected:
            self.base_path = folder_selected
            self._reload_folders()

    def _reload_folders(self):
        """Reload folders from current base path."""
        # Clear existing checkboxes
        for widget in self.folder_scroll.winfo_children():
            widget.destroy()
        self.folder_checkboxes.clear()

        # Update path label
        self.path_label.configure(text=f"Base: {self.base_path}")

        # Validate and potentially fix the path
        valid_path = self.processor.validate_and_fix_path(self.base_path)
        if valid_path and valid_path != self.base_path:
            self.base_path = valid_path
            self.path_label.configure(text=f"Base: {self.base_path}")

        # Load folders
        self._load_folders()

    def _load_folders(self):
        """Load folders from base path."""
        folders = self.processor.get_folders_in_directory(self.base_path)

        for folder_path in folders:
            folder_name = Path(folder_path).name
            var = ctk.BooleanVar()

            checkbox = ctk.CTkCheckBox(
                self.folder_scroll,
                text=folder_name,
                variable=var,
                font=ctk.CTkFont(size=12)
            )
            checkbox.pack(anchor="w", padx=10, pady=5)

            self.folder_checkboxes[folder_name] = var

        # Update folder count
        if folders:
            self.folder_count_label.configure(text=f"Found {len(folders)} folder(s)")
        else:
            self.folder_count_label.configure(text="No folders found")
            ctk.CTkLabel(
                self.folder_scroll,
                text="No folders found in base directory",
                text_color="gray"
            ).pack(padx=10, pady=10)

    def _get_selected_folders(self) -> List[str]:
        """Get list of selected folder names."""
        selected = []
        for folder_name, var in self.folder_checkboxes.items():
            if var.get():
                selected.append(folder_name)
        return selected

    def _set_button_states_idle(self):
        """Set button states for idle (ready to start)."""
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled", text="⏸ Pause")
        self.stop_button.configure(state="disabled")
        self.browse_button.configure(state="normal")
        self.quit_button.configure(state="normal")

    def _set_button_states_processing(self):
        """Set button states for active processing."""
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal", text="⏸ Pause")
        self.stop_button.configure(state="normal")
        self.browse_button.configure(state="disabled")
        self.quit_button.configure(state="disabled")

    def _set_button_states_paused(self):
        """Set button states for paused state."""
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal", text="▶ Resume")
        self.stop_button.configure(state="normal")
        self.browse_button.configure(state="disabled")
        self.quit_button.configure(state="disabled")

    def _start_processing(self):
        """Start the batch processing."""
        self.selected_folders = self._get_selected_folders()

        if not self.selected_folders:
            messagebox.showwarning("No Selection", "Please select at least one folder to process.")
            return

        # Clear log
        self.log_text.delete("1.0", "end")

        # Reset progress
        self.progress_bar.set(0)
        self.start_time = time.time()

        # Update button states to processing
        self._set_button_states_processing()

        # Disable folder selection and delete checkbox
        for checkbox in self.folder_scroll.winfo_children():
            if isinstance(checkbox, ctk.CTkCheckBox):
                checkbox.configure(state="disabled")
        self.delete_checkbox.configure(state="disabled")

        # Get deletion preference
        delete_source = self.delete_source_var.get()

        # Start processing in thread
        self.processing_thread = threading.Thread(
            target=self.processor.process_folders,
            args=(self.selected_folders, self.base_path, delete_source),
            daemon=True
        )
        self.processing_thread.start()

        # Start time updater
        self._update_time()

    def _pause_processing(self):
        """Pause or resume processing."""
        if self.processor.is_paused:
            self.processor.resume()
            self._set_button_states_processing()
            self._log_message("Processing resumed")
        else:
            self.processor.pause()
            self._set_button_states_paused()
            self._log_message("Processing paused")

    def _stop_processing(self):
        """Stop processing."""
        if messagebox.askyesno("Confirm Stop", "Are you sure you want to stop processing?"):
            self.processor.stop()
            self._log_message("Stopping processing...")
            self.stop_button.configure(state="disabled")

    def _on_progress_update(self, current: int, total: int, message: str):
        """Handle progress updates from processor."""
        def update():
            progress = current / total if total > 0 else 0
            self.progress_bar.set(progress)
            self.progress_label.configure(text=message)

        self.after(0, update)

    def _on_log_message(self, message: str):
        """Handle log messages from processor."""
        self.after(0, lambda: self._log_message(message))

    def _log_message(self, message: str):
        """Add message to log."""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

        # Check if processing is complete
        if not self.processor.is_running and self.processing_thread is not None:
            self._on_processing_complete()

    def _update_time(self):
        """Update elapsed and estimated time."""
        if not self.processor.is_running:
            return

        if self.start_time:
            elapsed = time.time() - self.start_time
            elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))

            # Estimate completion time
            progress = self.progress_bar.get()
            if progress > 0 and not self.processor.is_paused:
                total_estimated = elapsed / progress
                remaining = total_estimated - elapsed
                remaining_str = time.strftime("%H:%M:%S", time.gmtime(remaining))
            else:
                remaining_str = "--:--:--"

            self.time_label.configure(text=f"Elapsed: {elapsed_str} | Estimated: {remaining_str}")

        # Schedule next update
        self.after(1000, self._update_time)

    def _on_processing_complete(self):
        """Handle processing completion."""
        # Update button states to idle
        self._set_button_states_idle()

        # Re-enable folder selection and delete checkbox
        for checkbox in self.folder_scroll.winfo_children():
            if isinstance(checkbox, ctk.CTkCheckBox):
                checkbox.configure(state="normal")
        self.delete_checkbox.configure(state="normal")

        # Show completion message
        elapsed = time.time() - self.start_time if self.start_time else 0
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))

        messagebox.showinfo(
            "Processing Complete",
            f"Batch processing completed!\nTotal time: {elapsed_str}"
        )

    def _quit_application(self):
        """Quit the application with confirmation if processing."""
        if self.processor.is_running:
            if messagebox.askyesno(
                "Confirm Exit",
                "Processing is currently running. Do you want to stop and exit?"
            ):
                self.processor.stop()
                self.destroy()
        else:
            if messagebox.askyesno(
                "Confirm Exit",
                "Are you sure you want to exit the application?"
            ):
                self.destroy()

    def on_closing(self):
        """Clean up before closing (window close button)."""
        self._quit_application()


def run_batch_app():
    """Run the Batch PDF Joiner application."""
    app = BatchPDFJoinerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
