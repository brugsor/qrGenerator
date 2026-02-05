import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import qrcode
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import io
import win32clipboard
import textwrap

OUTPUT_DIR = "generatedQRs"
LOGO_PATH = "sources\Prysmian_Logo_CMYK_Positive.jpg"


class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("500x600")
        self.root.resizable(True, True)

        self.current_qr_image = None
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
        input_label = ttk.Label(main_frame, text="Enter text to encode:")
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

        # QR Code preview section
        preview_label = ttk.Label(main_frame, text="Preview:")
        preview_label.pack(anchor=tk.W, pady=(20, 5))

        # Canvas for QR code display with border
        self.canvas_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=2)
        self.canvas_frame.pack(pady=10)

        self.qr_canvas = tk.Canvas(
            self.canvas_frame,
            width=300,
            height=300,
            bg="white"
        )
        self.qr_canvas.pack()

        # Status label
        self.status_var = tk.StringVar(value="Enter text and click 'Generate QR Code'")
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9)
        )
        self.status_label.pack(pady=10)

        # Bind Enter key to generate
        self.root.bind('<Control-Return>', lambda e: self.generate_qr())

    def generate_qr(self):
        text = self.text_input.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Warning", "Please enter some text to encode.")
            return

        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            # Create QR image
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

            self.current_qr_image = final_img

            # Convert for display (resize to fit preview)
            display_image = final_img.copy()
            display_ratio = min(300 / final_img.width, 300 / final_img.height)
            display_size = (int(final_img.width * display_ratio), int(final_img.height * display_ratio))
            display_image = display_image.resize(display_size, Image.Resampling.LANCZOS)

            self.photo = ImageTk.PhotoImage(display_image)

            # Update canvas
            self.qr_canvas.delete("all")
            self.qr_canvas.create_image(150, 150, image=self.photo)

            # Enable save and copy buttons
            self.save_btn.configure(state=tk.NORMAL)
            self.copy_btn.configure(state=tk.NORMAL)

            # Update status
            char_count = len(text)
            self.status_var.set(f"QR code generated successfully! ({char_count} characters)")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code:\n{str(e)}")

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
        self.save_btn.configure(state=tk.DISABLED)
        self.copy_btn.configure(state=tk.DISABLED)
        self.status_var.set("Enter text and click 'Generate QR Code'")


def main():
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
