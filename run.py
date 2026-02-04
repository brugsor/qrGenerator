import qrcode

# Lista de strings que quieres convertir en QR
strings = ["Hola mundo,como se llama tu mamá,1'34098130948", "https://microsoft.com", "Texto de prueba"]

# Generar un QR por cada string
for i, text in enumerate(strings, start=1):
    # Crear objeto QR
    qr = qrcode.QRCode(
        version=1,  # tamaño del QR (1 es el más pequeño)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # nivel de corrección de errores
        box_size=10,  # tamaño de cada "cuadro"
        border=4,  # grosor del borde
    )
    
    # Agregar el texto al QR
    qr.add_data(text)
    qr.make(fit=True)

    # Crear imagen del QR
    img = qr.make_image(fill_color="black", back_color="white")

    # Guardar el archivo con un nombre único
    img.save(f"qr_code_{i}.png")

print("✅ Códigos QR generados y guardados como imágenes.")
