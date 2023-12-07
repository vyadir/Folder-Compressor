# Importar las bibliotecas necesarias
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import shutil
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import dotenv  # Para cargar las variables de entorno desde un archivo .env

# Cargar las variables de entorno desde el archivo .env
dotenv.load_dotenv()

# Definir una clase para la aplicación del compresor
class CompressorApp:
    def __init__(self, root):
        # Inicializar la aplicación con la ventana principal
        self.root = root
        self.root.title("Compresor de Directorios")
        self.root.geometry("800x400")
        self.root.configure(bg="lightblue")
        self.root.resizable(False, False)

        # Centrar la ventana en la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (800 / 2)
        y = (screen_height / 2) - (400 / 2)
        self.root.geometry(f'+{int(x)}+{int(y)}')

        # ComboBox para seleccionar el formato de compresión
        self.formats = ["ZIP", "TAR", "TAR.GZ", "TAR.BZ2", "XZTAR"]
        self.format_label = tk.Label(self.root, text="Selecciona un formato de compresión:", font=("Arial", 14), bg="lightblue")
        self.format_label.pack()
        self.format_combo = ttk.Combobox(self.root, values=self.formats, font=("Arial", 12))
        self.format_combo.pack(pady=5)
        self.format_combo.set(self.formats[0])

        # Botón para comprimir el directorio
        self.compress_button = tk.Button(self.root, text="Comprimir y Enviar por Correo", command=self.compress_and_send, font=("Arial", 14), bg="green", fg="white")
        self.compress_button.pack(pady=10)

        # Etiqueta para mostrar el resultado
        self.result_label = tk.Label(self.root, text="", font=("Arial", 12), bg="lightblue")
        self.result_label.pack()

    def compress_and_send(self):
        # Función para comprimir y enviar el directorio seleccionado
        folder_path = filedialog.askdirectory(title="Selecciona un directorio para comprimir")
        
        if folder_path:
            selected_format = self.format_combo.get()
            format_extensions = {
                "ZIP": "zip",
                "TAR": "tar",
                "TAR.GZ": "gztar",
                "TAR.BZ2": "bztar",
                "XZTAR": "xztar"
            }
            
            if selected_format in format_extensions:
                zip_filename = os.path.basename(folder_path)
                destination_folder = filedialog.askdirectory(title="Selecciona una ubicación de destino para guardar el archivo comprimido")
                
                if destination_folder:
                    # Crear un archivo comprimido en el formato seleccionado
                    shutil.make_archive(os.path.join(destination_folder, zip_filename), format_extensions[selected_format], folder_path)
                    
                    # Enviar el archivo por correo electrónico
                    if self.send_email(destination_folder, zip_filename):
                        self.result_label.config(text=f"Archivo comprimido y enviado por correo electrónico correctamente.", fg="green")
                    else:
                        self.result_label.config(text="Error al enviar el correo electrónico.", fg="red")
                else:
                    self.result_label.config(text="Error: No se seleccionó una ubicación de destino para guardar.", fg="red")
            else:
                self.result_label.config(text="Error: Formato de compresión no válido.", fg="red")
        else:
            self.result_label.config(text="Error: No se seleccionó un directorio.", fg="red")

    def send_email(self, folder_path, filename):
        # Función para enviar el archivo comprimido por correo electrónico
        try:
            # Configuración del servidor SMTP
            smtp_server = os.getenv("SMTP_SERVIDOR")
            smtp_port = int(os.getenv("SMTP_PUERTO"))
            smtp_user = os.getenv("SMTP_USUARIO")
            smtp_password = os.getenv("SMTP_PASSWORD")

            # Crear una conexión SMTP segura con Gmail
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)

            # Crear el mensaje de correo
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = smtp_user  # Enviar el correo a ti mismo
            msg["Subject"] = f"Archivo comprimido: {filename}"

            # Adjuntar el archivo comprimido al mensaje
            file_path = os.path.join(folder_path, f"{filename}.{self.format_combo.get()}")
            attachment = open(file_path, "rb")
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}.{self.format_combo.get()}")
            msg.attach(part)

            # Enviar el mensaje
            server.sendmail(smtp_user, smtp_user, msg.as_string())
            server.quit()

            return True
        except Exception as e:
            print(f"Error al enviar el correo electrónico: {str(e)}")
            return False

if __name__ == "__main__":
    # Iniciar la aplicación
    root = tk.Tk()
    app = CompressorApp(root)
    root.mainloop()
