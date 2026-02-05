import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import qrcode
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import io
import win32clipboard
import textwrap
import zipfile
import threading
from datetime import datetime

OUTPUT_DIR = "generatedQRs"
LOGO_PATH = "sources\Prysmian_Logo_CMYK_Positive.jpg"


class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("600x800")
        self.root.resizable(True, True)

        self.current_qr_image = None
        self.strings_list = []
        self.current_index = 0
        self.setup_ui()

    def setup_ui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        title_label = ttk.Label(
            main_frame,
            text="QR Code Generator",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Input section
        input_label = ttk.Label(main_frame, text="Enter text to encode (one per line for batch):")
        input_label.pack(anchor=tk.W)

        # Text input with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.X, pady=(5, 15))

        self.text_input = tk.Text(
            text_frame,
            height=5,
            width=50,
            font=("Consolas", 11),
            wrap=tk.WORD
        )
        scrollbar = ttk.Scrollbar(text_frame, command=self.text_input.yview)
        self.text_input.configure(yscrollcommand=scrollbar.set)

        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=10)

        self.generate_btn = ttk.Button(
            buttons_frame,
            text="Generate QR Code",
            command=self.generate_qr
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(
            buttons_frame,
            text="Save QR Code",
            command=self.save_qr,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.copy_btn = ttk.Button(
            buttons_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard,
            state=tk.DISABLED
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(
            buttons_frame,
            text="Clear",
            command=self.clear_all
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Second row of buttons
        buttons_frame2 = ttk.Frame(main_frame)
        buttons_frame2.pack(pady=(0, 10))

        self.load_file_btn = ttk.Button(
            buttons_frame2,
            text="Load from File",
            command=self._load_from_file
        )
        self.load_file_btn.pack(side=tk.LEFT, padx=5)

        self.export_zip_btn = ttk.Button(
            buttons_frame2,
            text="Export All as ZIP",
            command=self._export_all_zip,
            state=tk.DISABLED
        )
        self.export_zip_btn.pack(side=tk.LEFT, padx=5)

        # Navigation bar
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(pady=(0, 5))

        self.prev_btn = ttk.Button(
            nav_frame,
            text="< Prev",
            command=self._show_prev,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.nav_label_var = tk.StringVar(value="")
        self.nav_label = ttk.Label(
            nav_frame,
            textvariable=self.nav_label_var,
            font=("Segoe UI", 10, "bold"),
            width=12,
            anchor=tk.CENTER
        )
        self.nav_label.pack(side=tk.LEFT, padx=10)

        self.next_btn = ttk.Button(
            nav_frame,
            text="Next >",
            command=self._show_next,
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # QR Code preview section
        preview_label = ttk.Label(main_frame, text="Preview:")
        preview_label.pack(anchor=tk.W, pady=(20, 5))

        # Canvas for QR code display with border and scrollbars
        self.canvas_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=2)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.qr_canvas = tk.Canvas(
            self.canvas_frame,
            bg="white"
        )

        canvas_vscroll = ttk.Scrollbar(
            self.canvas_frame, orient=tk.VERTICAL, command=self.qr_canvas.yview
        )
        canvas_hscroll = ttk.Scrollbar(
            self.canvas_frame, orient=tk.HORIZONTAL, command=self.qr_canvas.xview
        )
        self.qr_canvas.configure(
            yscrollcommand=canvas_vscroll.set,
            xscrollcommand=canvas_hscroll.set
        )

        canvas_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        canvas_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.qr_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Status label
        self.status_var = tk.StringVar(value="Enter text and click 'Generate QR Code'")
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9)
        )
        self.status_label.pack(pady=(5, 0))

        # Bind Enter key to generate
        self.root.bind('<Control-Return>', lambda e: self.generate_qr())

        # Re-render preview when canvas is resized
        self._resize_after_id = None
        self.qr_canvas.bind('<Configure>', self._on_canvas_resize)

    def _build_qr_image(self, text):
        """Build a QR code image for the given text and return it as a PIL Image."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_size = qr_img.size[0]

        # Load and resize logo
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_width = 250
        logo_height = int(logo.height * (logo_width / logo.width))
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Calculate text dimensions
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        # Wrap text to fit within image width
        max_text_width = max(qr_size, 400)
        wrapped_text = textwrap.fill(text, width=50)

        # Create temporary image to measure text
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        text_bbox = temp_draw.textbbox((0, 0), wrapped_text, font=font)
        text_height = text_bbox[3] - text_bbox[1]
        text_width = text_bbox[2] - text_bbox[0]

        # Calculate final image dimensions
        padding = 30
        logo_padding = 20
        canvas_width = max(qr_size, text_width, logo_width) + (padding * 2)
        canvas_height = logo_height + logo_padding + qr_size + padding + text_height + (padding * 2)

        # Create final canvas
        final_img = Image.new("RGB", (canvas_width, canvas_height), "white")

        # Paste logo at top left
        final_img.paste(logo, (padding, padding), logo)

        # Calculate QR position (centered horizontally, below logo)
        qr_x = (canvas_width - qr_size) // 2
        qr_y = logo_height + logo_padding + padding
        final_img.paste(qr_img, (qr_x, qr_y))

        # Add text below QR code
        draw = ImageDraw.Draw(final_img)
        text_x = (canvas_width - text_width) // 2
        text_y = qr_y + qr_size + padding
        draw.text((text_x, text_y), wrapped_text, fill="black", font=font)

        return final_img

    def generate_qr(self):
        raw_text = self.text_input.get("1.0", tk.END)
        lines = [line.strip() for line in raw_text.splitlines()]
        lines = [line for line in lines if line]

        if not lines:
            messagebox.showwarning("Warning", "Please enter some text to encode.")
            return

        if len(lines) > 2000:
            messagebox.showwarning(
                "Warning",
                f"Too many strings ({len(lines)}). Maximum is 2000. "
                "Please reduce the number of lines."
            )
            return

        self.strings_list = lines
        self.current_index = 0

        try:
            self.current_qr_image = self._build_qr_image(self.strings_list[0])
            self._update_preview()

            # Enable save and copy buttons
            self.save_btn.configure(state=tk.NORMAL)
            self.copy_btn.configure(state=tk.NORMAL)

            # Enable export ZIP
            self.export_zip_btn.configure(state=tk.NORMAL)

            # Update navigation
            self._update_nav_state()

            # Update status
            n = len(self.strings_list)
            if n == 1:
                char_count = len(self.strings_list[0])
                self.status_var.set(f"QR code generated successfully! ({char_count} characters)")
            else:
                self.status_var.set(f"Showing 1 / {n}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code:\n{str(e)}")

    def _update_nav_state(self):
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

    def _show_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            try:
                self.current_qr_image = self._build_qr_image(
                    self.strings_list[self.current_index]
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

    def _show_next(self):
        if self.current_index < len(self.strings_list) - 1:
            self.current_index += 1
            try:
                self.current_qr_image = self._build_qr_image(
                    self.strings_list[self.current_index]
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

    def _export_all_zip(self):
        if not self.strings_list:
            messagebox.showwarning("Warning", "No QR codes to export. Generate first.")
            return

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"qr_export_{timestamp}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_filename)

        total = len(self.strings_list)

        # Create progress window
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Exporting QR Codes")
        progress_win.geometry("350x130")
        progress_win.resizable(False, False)
        progress_win.transient(self.root)
        progress_win.grab_set()

        ttk.Label(
            progress_win,
            text=f"Exporting {total} QR code(s)...",
            font=("Segoe UI", 10)
        ).pack(pady=(15, 5))

        progress_var = tk.DoubleVar(value=0)
        progress_bar = ttk.Progressbar(
            progress_win, variable=progress_var, maximum=total, length=280
        )
        progress_bar.pack(pady=5, padx=20)

        progress_label_var = tk.StringVar(value=f"0 / {total}")
        ttk.Label(progress_win, textvariable=progress_label_var).pack()

        cancel_flag = threading.Event()

        def on_cancel():
            cancel_flag.set()

        cancel_btn = ttk.Button(progress_win, text="Cancel", command=on_cancel)
        cancel_btn.pack(pady=(5, 10))

        def export_thread():
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for i, text in enumerate(self.strings_list):
                        if cancel_flag.is_set():
                            break

                        img = self._build_qr_image(text)
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        entry_name = f"qr_{i + 1:04d}.png"
                        zf.writestr(entry_name, buf.getvalue())

                        # Update progress on the main thread
                        self.root.after(0, lambda idx=i: _update_progress(idx + 1))

                if cancel_flag.is_set():
                    # Clean up partial zip
                    try:
                        os.remove(zip_path)
                    except OSError:
                        pass
                    self.root.after(0, lambda: _finish_cancelled())
                else:
                    self.root.after(0, lambda: _finish_success())

            except Exception as e:
                # Clean up on error
                try:
                    os.remove(zip_path)
                except OSError:
                    pass
                self.root.after(0, lambda err=str(e): _finish_error(err))

        def _update_progress(count):
            progress_var.set(count)
            progress_label_var.set(f"{count} / {total}")

        def _finish_success():
            progress_win.destroy()
            abs_path = os.path.abspath(zip_path)
            self.status_var.set(f"Exported {total} QR codes to {zip_filename}")
            messagebox.showinfo(
                "Export Complete",
                f"Successfully exported {total} QR code(s) to:\n{abs_path}"
            )

        def _finish_cancelled():
            progress_win.destroy()
            self.status_var.set("Export cancelled.")

        def _finish_error(err):
            progress_win.destroy()
            messagebox.showerror("Export Error", f"Failed to export:\n{err}")

        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()

    def _load_from_file(self):
        filepath = filedialog.askopenfilename(
            title="Select file to load",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_input.delete("1.0", tk.END)
                self.text_input.insert("1.0", content)
                line_count = len([l for l in content.splitlines() if l.strip()])
                self.status_var.set(f"Loaded {line_count} line(s) from {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def _update_preview(self):
        if self.current_qr_image is None:
            return

        canvas_w = self.qr_canvas.winfo_width()
        canvas_h = self.qr_canvas.winfo_height()

        # Avoid degenerate sizes before the widget is mapped
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

    def _on_canvas_resize(self, event):
        # Debounce resize events
        if self._resize_after_id is not None:
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(100, self._update_preview)

    def save_qr(self):
        if self.current_qr_image is None:
            messagebox.showwarning("Warning", "No QR code to save. Generate one first.")
            return

        # Ask user for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ],
            initialdir=OUTPUT_DIR,
            initialfile="qr_code.png"
        )

        if filepath:
            try:
                os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
                self.current_qr_image.save(filepath)
                self.status_var.set(f"Saved: {filepath}")
                messagebox.showinfo("Success", f"QR code saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")

    def copy_to_clipboard(self):
        if self.current_qr_image is None:
            messagebox.showwarning("Warning", "No QR code to copy. Generate one first.")
            return

        try:
            # Convert image to BMP format for Windows clipboard
            output = io.BytesIO()
            # Convert to RGB if necessary and save as BMP
            image = self.current_qr_image.convert("RGB")
            image.save(output, format="BMP")
            bmp_data = output.getvalue()[14:]  # Remove BMP file header

            # Copy to clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, bmp_data)
            win32clipboard.CloseClipboard()

            self.status_var.set("QR code copied to clipboard!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{str(e)}")

    def clear_all(self):
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


def main():
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
