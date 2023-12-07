import shutil
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import dotenv

# Cargar las variables de entorno desde el archivo .env
dotenv.load_dotenv()

class DirectoryCompressor:
    """Clase para comprimir directorios y enviarlos por correo electrónico."""

    def __init__(self):
        """Inicializa la clase con configuraciones de formato."""
        self.format_extensions = {
            "ZIP": "zip",
            "TAR": "tar",
            "TAR.GZ": "gztar",
            "TAR.BZ2": "bztar",
            "XZTAR": "xztar"
        }

    def compress_directory(self, folder_path, selected_format, destination_folder):
        """
        Comprime un directorio en un formato especificado y lo guarda en una ubicación de destino.
        """
        try:
            # Verifica si el formato seleccionado es válido
            if selected_format in self.format_extensions:
                zip_filename = os.path.basename(folder_path)
                # Comprime el directorio
                shutil.make_archive(os.path.join(destination_folder, zip_filename), 
                                    self.format_extensions[selected_format], folder_path)
                return zip_filename
            else:
                print("Error: Formato de compresión no válido o no seleccionado.")
                return None
        except Exception as e:
            print(f"Error al comprimir el directorio: {str(e)}")
            return None

class EmailSender:
    """Clase para enviar correos electrónicos."""

    def __init__(self):
        """Inicializa la clase con la configuración del servidor SMTP."""
        self.smtp_server = os.getenv("SMTP_SERVIDOR")
        self.smtp_port = int(os.getenv("SMTP_PUERTO"))
        self.smtp_user = os.getenv("SMTP_USUARIO")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    def send_email(self, folder_path, filename, file_extension):
        """
        Envia un archivo por correo electrónico.
        """
        try:
            # Crear una conexión SMTP segura
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)

            # Crear el mensaje de correo
            msg = MIMEMultipart()
            msg["From"] = self.smtp_user
            msg["To"] = self.smtp_user  # Enviar el correo a ti mismo
            msg["Subject"] = f"Archivo comprimido: {filename}"

            # Adjuntar el archivo comprimido
            file_path = os.path.join(folder_path, f"{filename}.{file_extension}")
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename= {filename}.{file_extension}")
                msg.attach(part)

            # Enviar el mensaje
            server.sendmail(self.smtp_user, self.smtp_user, msg.as_string())
            server.quit()

            return True
        except Exception as e:
            print(f"Error al enviar el correo electrónico: {str(e)}")
            return False

def main():
    """
    Función principal para ejecutar el proceso de compresión y envío de correo.
    """
    print("Comenzando el proceso de compresión y envío de correo...")

    # Solicitar la ruta del directorio a comprimir
    folder_path = input("Ingresa la ruta del directorio a comprimir: ")

    if folder_path:
        print("Directorio seleccionado:", folder_path)

        # Opciones de formato de compresión
        formats = ["ZIP", "TAR", "TAR.GZ", "TAR.BZ2", "XZTAR"]
        print("Formatos disponibles: " + ", ".join(formats))
        selected_format = input("Selecciona un formato de compresión: ").upper()

        # Solicitar la ruta de destino
        destination_folder = input("Ingresa la ruta de la ubicación de destino para guardar el archivo comprimido: ")

        compressor = DirectoryCompressor()
        zip_filename = compressor.compress_directory(folder_path, selected_format, destination_folder)

        if zip_filename:
            print("Compresión completada.")
            email_sender = EmailSender()
            if email_sender.send_email(destination_folder, zip_filename, selected_format.lower()):
                print("Archivo comprimido y enviado por correo electrónico correctamente.")
            else:
                print("Error al enviar el correo electrónico.")
        else:
            print("Error en la compresión del directorio.")

if __name__ == "__main__":
    main()

