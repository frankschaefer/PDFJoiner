"""CustomTkinter GUI for PDF Joiner."""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List
from .pikepdf_merger import PikePDFMerger


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class PDFJoinerApp(ctk.CTk):
    """Main application window for PDF Joiner."""

    def __init__(self):
        super().__init__()

        self.title("PDF Joiner")
        self.geometry("800x600")

        self.pdf_files: List[str] = []
        self.merger = PikePDFMerger(quality="medium")

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self,
            text="PDF Joiner",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=20)

        # File list frame
        self.file_list_frame = ctk.CTkFrame(self)
        self.file_list_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.file_list_frame.grid_columnconfigure(0, weight=1)

        # File list label
        list_label = ctk.CTkLabel(
            self.file_list_frame,
            text="PDF Files (in order):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Scrollable file list
        self.file_listbox = ctk.CTkTextbox(
            self.file_list_frame,
            height=300
        )
        self.file_listbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.file_list_frame.grid_rowconfigure(1, weight=1)

        # Button frame
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, padx=20, pady=(0, 20))

        # Add files button
        add_button = ctk.CTkButton(
            button_frame,
            text="Add PDF Files",
            command=self._add_files,
            width=150
        )
        add_button.grid(row=0, column=0, padx=5)

        # Clear button
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear All",
            command=self._clear_files,
            width=150
        )
        clear_button.grid(row=0, column=1, padx=5)

        # Merge button
        merge_button = ctk.CTkButton(
            button_frame,
            text="Merge PDFs",
            command=self._merge_files,
            width=150,
            fg_color="green",
            hover_color="darkgreen"
        )
        merge_button.grid(row=0, column=2, padx=5)

    def _add_files(self):
        """Open file dialog to add PDF files."""
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if files:
            self.pdf_files.extend(files)
            self._update_file_list()

    def _clear_files(self):
        """Clear all selected files."""
        self.pdf_files.clear()
        self._update_file_list()

    def _update_file_list(self):
        """Update the file list display."""
        self.file_listbox.delete("1.0", "end")

        for i, file_path in enumerate(self.pdf_files, 1):
            filename = Path(file_path).name
            self.file_listbox.insert("end", f"{i}. {filename}\n")

    def _merge_files(self):
        """Merge the selected PDF files."""
        if not self.pdf_files:
            messagebox.showwarning("No Files", "Please add PDF files to merge.")
            return

        # Ask for output file location
        output_file = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not output_file:
            return

        # Perform merge
        success, error_message = self.merger.merge_pdfs(self.pdf_files, output_file)

        if success:
            messagebox.showinfo(
                "Success",
                f"PDFs merged successfully!\nSaved to: {output_file}"
            )
            self._clear_files()
        else:
            error_text = f"Failed to merge PDFs.\n\n{error_message}" if error_message else "Failed to merge PDFs. Please check the files and try again."
            messagebox.showerror(
                "Error",
                error_text
            )

    def on_closing(self):
        """Clean up before closing."""
        self.merger.close()
        self.destroy()


def run_app():
    """Run the PDF Joiner application."""
    app = PDFJoinerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
