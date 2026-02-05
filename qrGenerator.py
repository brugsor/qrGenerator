import qrcode
import sys
import os

OUTPUT_DIR = "sources"


def generate_qr_codes(strings: list[str]) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, text in enumerate(strings):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        filename = f"qr_{i + 1}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        img.save(filepath)
        print(f"[{i + 1}/{len(strings)}] Saved: {filepath}  ->  {text!r}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python qrGenerator.py <string1> <string2> ...")
        sys.exit(1)

    generate_qr_codes(sys.argv[1:])
