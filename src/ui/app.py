"""Main GUI application class.

This module contains the QRGeneratorApp class which manages the user interface
and coordinates between UI events and core business logic.
"""

import os
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from ..config import (
    DEFAULT_FONT,
    DEFAULT_HEIGHT_INCHES,
    DEFAULT_LOGO_ALIGN,
    DEFAULT_LOGO_PATH,
    DEFAULT_LOGO_WIDTH,
    DEFAULT_QR_ALIGN,
    DEFAULT_TEXT_ALIGN,
    DEFAULT_TEXT_SIZE,
    DEFAULT_WIDTH_INCHES,
    MAX_BATCH_SIZE,
    OUTPUT_DIR,
    OUTPUT_DPI,
)
from ..core import QRImageBuilder, export_qr_codes_to_zip, save_qr_image
from ..utils import clipboard, dimensions


class QRGeneratorApp:
    """Main application class for QR code generator GUI.

    This class manages the user interface and coordinates between UI events
    and the core QR generation logic. It maintains UI state and delegates
    business logic to the appropriate modules.
    """

    def __init__(self, root: tk.Tk):
        """Initialize the QR code generator application.

        Args:
            root: Root tkinter window
        """
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("600x960")
        self.root.resizable(True, True)

        # Application state
        self.current_qr_image: Image.Image | None = None
        self.strings_list: list[str] = []
        self.current_index = 0
        self.custom_logo_path: Path | None = None

        # Design settings (UI state variables)
        self.logo_align_var = tk.StringVar(value=DEFAULT_LOGO_ALIGN)
        self.qr_align_var = tk.StringVar(value=DEFAULT_QR_ALIGN)
        self.text_align_var = tk.StringVar(value=DEFAULT_TEXT_ALIGN)
        self.logo_size_var = tk.IntVar(value=DEFAULT_LOGO_WIDTH)
        self.qr_size_var = tk.IntVar(value=10)
        self.text_size_var = tk.IntVar(value=DEFAULT_TEXT_SIZE)
        self.font_var = tk.StringVar(value=DEFAULT_FONT)
        self.unit_var = tk.StringVar(value="in")
        self.width_var = tk.StringVar(value=str(DEFAULT_WIDTH_INCHES))
        self.height_var = tk.StringVar(value=str(DEFAULT_HEIGHT_INCHES))
        self.status_var = tk.StringVar(value="Enter text and click 'Generate QR Code'")
        self.logo_status_var = tk.StringVar(value="Using default logo")
        self.nav_label_var = tk.StringVar(value="")

        # Canvas resize debouncing
        self._resize_after_id: str | None = None

        # Build UI
        self.setup_ui()

    def setup_ui(self) -> None:
        """Build the user interface layout."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, text="QR Code Generator", style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))

        # Input section
        self._create_input_section(main_frame)

        # Action buttons
        self._create_button_section(main_frame)

        # Logo upload section
        self._create_logo_section(main_frame)

        # Navigation controls
        self._create_navigation_section(main_frame)

        # Design settings
        self._create_design_settings_section(main_frame)

        # Preview area
        self._create_preview_section(main_frame)

        # Status label
        self.status_label = ttk.Label(
            main_frame, textvariable=self.status_var, font=("Segoe UI", 9), style="TLabel"
        )
        self.status_label.pack(pady=(5, 0))

        # Keyboard shortcuts
        self.root.bind("<Control-Return>", lambda e: self.generate_qr())

    def _create_input_section(self, parent: ttk.Frame) -> None:
        """Create text input section.

        Args:
            parent: Parent frame to pack into
        """
        input_label = ttk.Label(
            parent, text="Enter text to encode (one per line for batch):", style="TLabel"
        )
        input_label.pack(anchor=tk.W)

        text_frame = ttk.Frame(parent, style="TFrame")
        text_frame.pack(fill=tk.X, pady=(5, 15))

        self.text_input = tk.Text(
            text_frame,
            height=5,
            width=50,
            font=("Consolas", 11),
            wrap=tk.WORD,
            bg="white",
            fg="#1E293B",
            relief="solid",
            borderwidth=1,
            insertbackground="#2563EB",
        )
        scrollbar = ttk.Scrollbar(text_frame, command=self.text_input.yview)
        self.text_input.configure(yscrollcommand=scrollbar.set)

        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_button_section(self, parent: ttk.Frame) -> None:
        """Create action button section.

        Args:
            parent: Parent frame to pack into
        """
        # First row of buttons
        buttons_frame = ttk.Frame(parent, style="TFrame")
        buttons_frame.pack(pady=10)

        self.generate_btn = ttk.Button(
            buttons_frame,
            text="Generate QR Code",
            command=self.generate_qr,
            style="Primary.TButton",
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(
            buttons_frame,
            text="Save QR Code",
            command=self.save_qr,
            state=tk.DISABLED,
            style="Accent.TButton",
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.copy_btn = ttk.Button(
            buttons_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard,
            state=tk.DISABLED,
            style="Secondary.TButton",
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(
            buttons_frame, text="Clear", command=self.clear_all, style="Outline.TButton"
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Second row of buttons
        buttons_frame2 = ttk.Frame(parent, style="TFrame")
        buttons_frame2.pack(pady=(0, 10))

        self.load_file_btn = ttk.Button(
            buttons_frame2,
            text="Load from File",
            command=self._load_from_file,
            style="Secondary.TButton",
        )
        self.load_file_btn.pack(side=tk.LEFT, padx=5)

        self.export_zip_btn = ttk.Button(
            buttons_frame2,
            text="Export All as ZIP",
            command=self._export_all_zip,
            state=tk.DISABLED,
            style="Secondary.TButton",
        )
        self.export_zip_btn.pack(side=tk.LEFT, padx=5)

    def _create_logo_section(self, parent: ttk.Frame) -> None:
        """Create logo upload section.

        Args:
            parent: Parent frame to pack into
        """
        logo_frame = ttk.LabelFrame(
            parent, text="Logo Settings", padding="10", style="TLabelframe"
        )
        logo_frame.pack(fill=tk.X, pady=(5, 5))

        logo_controls = ttk.Frame(logo_frame, style="TFrame")
        logo_controls.pack(fill=tk.X)

        self.logo_upload_btn = ttk.Button(
            logo_controls,
            text="Upload Custom Logo",
            command=self._upload_logo,
            style="Secondary.TButton",
        )
        self.logo_upload_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.logo_reset_btn = ttk.Button(
            logo_controls,
            text="Reset to Default",
            command=self._reset_logo,
            style="Outline.TButton",
            state=tk.DISABLED,
        )
        self.logo_reset_btn.pack(side=tk.LEFT, padx=5)

        logo_status_label = ttk.Label(
            logo_controls,
            textvariable=self.logo_status_var,
            font=("Segoe UI", 8),
            foreground="#64748B",
        )
        logo_status_label.pack(side=tk.LEFT, padx=10)

    def _create_navigation_section(self, parent: ttk.Frame) -> None:
        """Create navigation controls for batch mode.

        Args:
            parent: Parent frame to pack into
        """
        nav_frame = ttk.Frame(parent, style="TFrame")
        nav_frame.pack(pady=(0, 5))

        self.prev_btn = ttk.Button(
            nav_frame, text="< Prev", command=self._show_prev, state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.nav_label = ttk.Label(
            nav_frame,
            textvariable=self.nav_label_var,
            font=("Segoe UI", 10, "bold"),
            width=12,
            anchor=tk.CENTER,
        )
        self.nav_label.pack(side=tk.LEFT, padx=10)

        self.next_btn = ttk.Button(
            nav_frame, text="Next >", command=self._show_next, state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

    def _create_design_settings_section(self, parent: ttk.Frame) -> None:
        """Create design customization controls.

        Args:
            parent: Parent frame to pack into
        """
        design_frame = ttk.LabelFrame(
            parent, text="Design Settings", padding="10", style="TLabelframe"
        )
        design_frame.pack(fill=tk.X, pady=(5, 5))

        # Column headers
        ttk.Label(design_frame, text="Align", font=("Segoe UI", 8, "bold")).grid(
            row=0, column=1, columnspan=3, pady=(0, 2)
        )
        ttk.Label(design_frame, text="Size", font=("Segoe UI", 8, "bold")).grid(
            row=0, column=4, columnspan=3, pady=(0, 2)
        )

        # Logo row
        ttk.Label(design_frame, text="Logo:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5)
        )
        for i, val in enumerate(("left", "center", "right")):
            ttk.Radiobutton(
                design_frame,
                text=val[0].upper(),
                variable=self.logo_align_var,
                value=val,
                width=2,
            ).grid(row=1, column=1 + i, padx=1)
        ttk.Label(design_frame, text="Width:").grid(row=1, column=4, padx=(10, 2))
        ttk.Entry(design_frame, textvariable=self.logo_size_var, width=5).grid(
            row=1, column=5
        )
        ttk.Label(design_frame, text="px").grid(row=1, column=6, sticky=tk.W)

        # QR Code row
        ttk.Label(design_frame, text="QR Code:").grid(
            row=2, column=0, sticky=tk.W, padx=(0, 5)
        )
        for i, val in enumerate(("left", "center", "right")):
            ttk.Radiobutton(
                design_frame,
                text=val[0].upper(),
                variable=self.qr_align_var,
                value=val,
                width=2,
            ).grid(row=2, column=1 + i, padx=1)
        ttk.Label(design_frame, text="Box size:").grid(row=2, column=4, padx=(10, 2))
        ttk.Entry(design_frame, textvariable=self.qr_size_var, width=5).grid(
            row=2, column=5
        )

        # Text row
        ttk.Label(design_frame, text="Text:").grid(
            row=3, column=0, sticky=tk.W, padx=(0, 5)
        )
        for i, val in enumerate(("left", "center", "right")):
            ttk.Radiobutton(
                design_frame,
                text=val[0].upper(),
                variable=self.text_align_var,
                value=val,
                width=2,
            ).grid(row=3, column=1 + i, padx=1)
        ttk.Label(design_frame, text="Font size:").grid(row=3, column=4, padx=(10, 2))
        ttk.Entry(design_frame, textvariable=self.text_size_var, width=5).grid(
            row=3, column=5
        )
        ttk.Label(design_frame, text="pt").grid(row=3, column=6, sticky=tk.W)

        # Font row
        ttk.Label(design_frame, text="Font:").grid(
            row=4, column=0, sticky=tk.W, padx=(0, 5)
        )
        font_combo = ttk.Combobox(
            design_frame,
            textvariable=self.font_var,
            values=["Arial", "Times New Roman", "Verdana"],
            state="readonly",
            width=18,
        )
        font_combo.grid(row=4, column=1, columnspan=3, sticky=tk.W, pady=(3, 0))

    def _create_preview_section(self, parent: ttk.Frame) -> None:
        """Create QR code preview section with dimension inputs.

        Args:
            parent: Parent frame to pack into
        """
        preview_label = ttk.Label(parent, text="Preview:", style="TLabel")
        preview_label.pack(anchor=tk.W, pady=(20, 5))

        # Grid container for preview + dimension inputs
        preview_area = ttk.Frame(parent, style="TFrame")
        preview_area.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        preview_area.columnconfigure(0, weight=1)
        preview_area.rowconfigure(0, weight=1)

        # Canvas for QR code display with scrollbars
        self.canvas_frame = ttk.Frame(preview_area, relief="solid", borderwidth=1)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")

        self.qr_canvas = tk.Canvas(self.canvas_frame, bg="white")

        canvas_vscroll = ttk.Scrollbar(
            self.canvas_frame, orient=tk.VERTICAL, command=self.qr_canvas.yview
        )
        canvas_hscroll = ttk.Scrollbar(
            self.canvas_frame, orient=tk.HORIZONTAL, command=self.qr_canvas.xview
        )
        self.qr_canvas.configure(
            yscrollcommand=canvas_vscroll.set, xscrollcommand=canvas_hscroll.set
        )

        canvas_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        canvas_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.qr_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Height input (to the right of preview)
        height_frame = ttk.Frame(preview_area, style="TFrame")
        height_frame.grid(row=0, column=1, sticky="n", padx=(10, 0))

        ttk.Label(
            height_frame, text="Height:", font=("Segoe UI", 9), style="TLabel"
        ).pack(anchor=tk.W)
        height_entry = ttk.Entry(
            height_frame, textvariable=self.height_var, width=6, style="TEntry"
        )
        height_entry.pack(anchor=tk.W, pady=(2, 0))
        ttk.Label(
            height_frame, textvariable=self.unit_var, font=("Segoe UI", 8), style="TLabel"
        ).pack(anchor=tk.W)

        # Width input (below preview)
        width_frame = ttk.Frame(preview_area, style="TFrame")
        width_frame.grid(row=1, column=0, sticky="w", pady=(5, 0))

        ttk.Label(width_frame, text="Width:", font=("Segoe UI", 9), style="TLabel").pack(
            side=tk.LEFT
        )
        width_entry = ttk.Entry(
            width_frame, textvariable=self.width_var, width=6, style="TEntry"
        )
        width_entry.pack(side=tk.LEFT, padx=(5, 5))
        unit_combo = ttk.Combobox(
            width_frame,
            textvariable=self.unit_var,
            values=["cm", "in", "px"],
            state="readonly",
            width=4,
            style="TCombobox",
        )
        unit_combo.pack(side=tk.LEFT)

        # Bind canvas resize event
        self.qr_canvas.bind("<Configure>", self._on_canvas_resize)

    def _get_logo_path(self) -> Path:
        """Return the active logo path (custom or default).

        Returns:
            Path to logo file
        """
        if self.custom_logo_path and self.custom_logo_path.exists():
            return self.custom_logo_path
        return DEFAULT_LOGO_PATH

    def _get_qr_builder(self) -> QRImageBuilder:
        """Create QR image builder with current settings.

        Returns:
            Configured QRImageBuilder instance
        """
        return QRImageBuilder(
            logo_path=self._get_logo_path(),
            logo_align=self.logo_align_var.get(),  # type: ignore
            qr_align=self.qr_align_var.get(),  # type: ignore
            text_align=self.text_align_var.get(),  # type: ignore
            logo_width=self.logo_size_var.get(),
            qr_box_size=self.qr_size_var.get(),
            text_size=self.text_size_var.get(),
            font_name=self.font_var.get(),
        )

    def _upload_logo(self) -> None:
        """Allow user to select a custom logo file."""
        filepath = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*"),
            ],
        )
        if filepath:
            try:
                # Validate that it's a readable image
                test_img = Image.open(filepath)
                test_img.close()
                self.custom_logo_path = Path(filepath)
                filename = self.custom_logo_path.name
                self.logo_status_var.set(f"Using: {filename}")
                self.logo_reset_btn.configure(state=tk.NORMAL)
                self.status_var.set(f"Custom logo loaded: {filename}")
            except Exception as e:
                messagebox.showerror(
                    "Invalid Logo",
                    f"Failed to load image:\n{str(e)}\n\nPlease select a valid image file.",
                )

    def _reset_logo(self) -> None:
        """Reset to the default logo."""
        self.custom_logo_path = None
        self.logo_status_var.set("Using default logo")
        self.logo_reset_btn.configure(state=tk.DISABLED)
        self.status_var.set("Reset to default logo")

    def generate_qr(self) -> None:
        """Generate QR code(s) from text input."""
        raw_text = self.text_input.get("1.0", tk.END)
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        if not lines:
            messagebox.showwarning("Warning", "Please enter some text to encode.")
            return

        if len(lines) > MAX_BATCH_SIZE:
            messagebox.showwarning(
                "Warning",
                f"Too many strings ({len(lines)}). Maximum is {MAX_BATCH_SIZE}. "
                "Please reduce the number of lines.",
            )
            return

        try:
            width_val = float(self.width_var.get())
            height_val = float(self.height_var.get())
            target_w, target_h = dimensions.convert_to_pixels(
                width_val, height_val, self.unit_var.get()  # type: ignore
            )
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.strings_list = lines
        self.current_index = 0

        try:
            builder = self._get_qr_builder()
            self.current_qr_image = builder.build_image(self.strings_list[0], target_w, target_h)
            self._update_preview()

            # Enable buttons
            self.save_btn.configure(state=tk.NORMAL)
            self.copy_btn.configure(state=tk.NORMAL)
            self.export_zip_btn.configure(state=tk.NORMAL)

            # Update navigation
            self._update_nav_state()

            # Update status
            n = len(self.strings_list)
            if n == 1:
                char_count = len(self.strings_list[0])
                self.status_var.set(
                    f"QR code generated successfully! ({char_count} characters)"
                )
            else:
                self.status_var.set(f"Showing 1 / {n}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code:\n{str(e)}")

    def _update_nav_state(self) -> None:
        """Update navigation buttons and label based on current state."""
        n = len(self.strings_list)
        if n <= 1:
            self.prev_btn.configure(state=tk.DISABLED)
            self.next_btn.configure(state=tk.DISABLED)
            self.nav_label_var.set("")
        else:
            self.nav_label_var.set(f"{self.current_index + 1} / {n}")
            self.prev_btn.configure(
                state=tk.NORMAL if self.current_index > 0 else tk.DISABLED
            )
            self.next_btn.configure(
                state=tk.NORMAL if self.current_index < n - 1 else tk.DISABLED
            )

    def _show_prev(self) -> None:
        """Navigate to previous QR code in batch."""
        if self.current_index > 0:
            self.current_index -= 1
            self._regenerate_current()

    def _show_next(self) -> None:
        """Navigate to next QR code in batch."""
        if self.current_index < len(self.strings_list) - 1:
            self.current_index += 1
            self._regenerate_current()

    def _regenerate_current(self) -> None:
        """Regenerate QR code for current index."""
        try:
            width_val = float(self.width_var.get())
            height_val = float(self.height_var.get())
            target_w, target_h = dimensions.convert_to_pixels(
                width_val, height_val, self.unit_var.get()  # type: ignore
            )

            builder = self._get_qr_builder()
            self.current_qr_image = builder.build_image(
                self.strings_list[self.current_index], target_w, target_h
            )
            self._update_preview()
            self._update_nav_state()

            n = len(self.strings_list)
            self.status_var.set(
                f"Showing {self.current_index + 1} / {n} — "
                f"{self.strings_list[self.current_index][:50]}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code:\n{str(e)}")

    def _update_preview(self) -> None:
        """Update the preview canvas with current QR image."""
        if self.current_qr_image is None:
            return

        canvas_w = self.qr_canvas.winfo_width()
        canvas_h = self.qr_canvas.winfo_height()

        # Avoid degenerate sizes before widget is mapped
        if canvas_w < 10 or canvas_h < 10:
            return

        img = self.current_qr_image
        ratio = min(canvas_w / img.width, canvas_h / img.height)

        # Don't upscale beyond original size
        if ratio > 1:
            ratio = 1.0

        display_w = int(img.width * ratio)
        display_h = int(img.height * ratio)
        display_image = img.resize((display_w, display_h), Image.Resampling.LANCZOS)

        self.photo = ImageTk.PhotoImage(display_image)

        self.qr_canvas.delete("all")
        self.qr_canvas.configure(scrollregion=(0, 0, display_w, display_h))
        self.qr_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def _on_canvas_resize(self, event: tk.Event) -> None:
        """Handle canvas resize events with debouncing.

        Args:
            event: Tkinter event object
        """
        # Debounce resize events
        if self._resize_after_id is not None:
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(100, self._update_preview)

    def save_qr(self) -> None:
        """Save current QR code to file."""
        if self.current_qr_image is None:
            messagebox.showwarning("Warning", "No QR code to save. Generate one first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*"),
            ],
            initialdir=str(OUTPUT_DIR),
            initialfile="qr_code.png",
        )

        if filepath:
            try:
                save_qr_image(self.current_qr_image, Path(filepath), OUTPUT_DPI)
                self.status_var.set(f"Saved: {filepath}")
                messagebox.showinfo("Success", f"QR code saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")

    def copy_to_clipboard(self) -> None:
        """Copy current QR code to clipboard."""
        if self.current_qr_image is None:
            messagebox.showwarning("Warning", "No QR code to copy. Generate one first.")
            return

        try:
            clipboard.copy_image_to_clipboard(self.current_qr_image)
            self.status_var.set("QR code copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{str(e)}")

    def _load_from_file(self) -> None:
        """Load text input from file."""
        filepath = filedialog.askopenfilename(
            title="Select file to load",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_input.delete("1.0", tk.END)
                self.text_input.insert("1.0", content)
                line_count = len([l for l in content.splitlines() if l.strip()])
                self.status_var.set(
                    f"Loaded {line_count} line(s) from {os.path.basename(filepath)}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def _export_all_zip(self) -> None:
        """Export all QR codes to ZIP archive."""
        if not self.strings_list:
            messagebox.showwarning("Warning", "No QR codes to export. Generate first.")
            return

        try:
            width_val = float(self.width_var.get())
            height_val = float(self.height_var.get())
            target_w, target_h = dimensions.convert_to_pixels(
                width_val, height_val, self.unit_var.get()  # type: ignore
            )
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"qr_export_{timestamp}.zip"
        zip_path = OUTPUT_DIR / zip_filename

        total = len(self.strings_list)

        # Create progress dialog
        progress_win = self._create_progress_dialog(total)
        progress_var = progress_win.winfo_children()[1].cget("variable")
        progress_label_var = progress_win.winfo_children()[2].cget("textvariable")
        cancel_flag = threading.Event()

        # Cancel button callback
        def on_cancel():
            cancel_flag.set()

        progress_win.winfo_children()[3].configure(command=on_cancel)

        # Build image generator for export
        builder = self._get_qr_builder()

        def image_builder(text: str) -> Image.Image:
            return builder.build_image(text, target_w, target_h)

        # Export thread
        def export_thread():
            try:
                success = export_qr_codes_to_zip(
                    self.strings_list,
                    zip_path,
                    image_builder,
                    progress_callback=lambda count: self.root.after(
                        0, lambda c=count: _update_progress(c)
                    ),
                    cancel_flag=lambda: cancel_flag.is_set(),
                )

                if success:
                    self.root.after(0, _finish_success)
                else:
                    self.root.after(0, _finish_cancelled)

            except Exception as e:
                self.root.after(0, lambda err=str(e): _finish_error(err))

        def _update_progress(count: int):
            progress_var.set(count)
            progress_label_var.set(f"{count} / {total}")

        def _finish_success():
            progress_win.destroy()
            abs_path = zip_path.resolve()
            self.status_var.set(f"Exported {total} QR codes to {zip_filename}")
            messagebox.showinfo(
                "Export Complete",
                f"Successfully exported {total} QR code(s) to:\n{abs_path}",
            )

        def _finish_cancelled():
            progress_win.destroy()
            self.status_var.set("Export cancelled.")

        def _finish_error(err: str):
            progress_win.destroy()
            messagebox.showerror("Export Error", f"Failed to export:\n{err}")

        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()

    def _create_progress_dialog(self, total: int) -> tk.Toplevel:
        """Create progress dialog window.

        Args:
            total: Total number of items to process

        Returns:
            Progress dialog window
        """
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Exporting QR Codes")
        progress_win.geometry("350x130")
        progress_win.resizable(False, False)
        progress_win.transient(self.root)
        progress_win.grab_set()

        ttk.Label(
            progress_win, text=f"Exporting {total} QR code(s)...", font=("Segoe UI", 10)
        ).pack(pady=(15, 5))

        progress_var = tk.DoubleVar(value=0)
        progress_bar = ttk.Progressbar(
            progress_win, variable=progress_var, maximum=total, length=280
        )
        progress_bar.pack(pady=5, padx=20)

        progress_label_var = tk.StringVar(value=f"0 / {total}")
        ttk.Label(progress_win, textvariable=progress_label_var).pack()

        cancel_btn = ttk.Button(progress_win, text="Cancel")
        cancel_btn.pack(pady=(5, 10))

        return progress_win

    def clear_all(self) -> None:
        """Clear all inputs and reset application state."""
        self.text_input.delete("1.0", tk.END)
        self.qr_canvas.delete("all")
        self.current_qr_image = None
        self.strings_list = []
        self.current_index = 0
        self.save_btn.configure(state=tk.DISABLED)
        self.copy_btn.configure(state=tk.DISABLED)
        self.export_zip_btn.configure(state=tk.DISABLED)
        self.prev_btn.configure(state=tk.DISABLED)
        self.next_btn.configure(state=tk.DISABLED)
        self.nav_label_var.set("")
        self.status_var.set("Enter text and click 'Generate QR Code'")
