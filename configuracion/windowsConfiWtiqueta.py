import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

def obtener_config_etiqueta_mm() -> tuple[float, float]:
    """
    Lee la configuración de la etiqueta en milímetros desde el JSON.
    Si el archivo no existe, lo crea con valores predeterminados.
    """
    appdata_path = os.environ.get('APPDATA')
    config_dir = os.path.join(appdata_path, "ZZZ")
    config_file = os.path.join(config_dir, "config_etiqueta.json")

    # Si la carpeta no existe, la crea
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Si el archivo no existe, lo crea con valores predeterminados
    if not os.path.exists(config_file):
        config = {"ancho": 76, "alto": 51}
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        print(f"Archivo de configuración creado en: {config_file}")
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        ancho_mm = config.get("ancho", 25)
        alto_mm = config.get("alto", 76)
        return ancho_mm, alto_mm
    except Exception as e:
        print(f"Error al leer configuración de etiqueta: {e}")
        return 76, 51  # valores por defecto en mm

def guardar_config_etiqueta_mm(ancho: float, alto: float) -> bool:
    """
    Guarda la configuración de etiqueta (ancho y alto en milímetros)
    en el archivo config_etiqueta.json ubicado en la carpeta "configuracion".
    """
    appdata_path = os.environ.get('APPDATA')
    config_dir = os.path.join(appdata_path, "ZZZ")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    config_file = os.path.join(config_dir, "config_etiqueta.json")
    config = {"ancho": ancho, "alto": alto}
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar configuración de etiqueta: {e}")
        return False

def mostrar_ventana_config_etiqueta(parent: tk.Tk) -> None:
    """
    Crea y muestra la ventana de configuración de tamaño de etiqueta.
    La ventana permite elegir un tamaño predefinido de una lista ordenada o
    ingresar un valor personalizado que se guardará en el JSON.
    """
    ventana = tk.Toplevel(parent)
    ventana.title("Configuración de Tamaño de Etiqueta")
    ventana.geometry("400x300")
    
    # Lista de tamaños predefinidos (ancho x alto en mm), ordenados de menor a mayor.
    opciones = [
        "25 x 76 mm",
        "31 x 22 mm",
        "32 x 25 mm",
        "38 x 25 mm",
        "39 x 25 mm",
        "51 x 25 mm",
        "51 x 32 mm",
        "57 x 19 mm",
        "57 x 32 mm",
        "57 x 51 mm",
        "58 x 40 mm",
        "70 x 30 mm",
        "70 x 32 mm",
        "70 x 38 mm",
        "76 x 25 mm",
        "76 x 51 mm",
        "76 x 76 mm",
        "76 x 102 mm",
        "100 x 50 mm",
        "101.6 x 50.8 mm",
        "102 x 25 mm",
        "102 x 38 mm",
        "102 x 51 mm",
        "102 x 64 mm",
        "102 x 102 mm",
        "102 x 127 mm",
        "102 x 150 mm",
        "102 x 152 mm",
        "102 x 165 mm",
        "102 x 210 mm",
        "105 x 148 mm",
        "148 x 210 mm",
        "152 x 216 mm"
    ]
    # Agregar opción para tamaño personalizado.
    opciones.append("Personalizado")
    
    # Mostrar configuración actual:
    ancho_actual, alto_actual = obtener_config_etiqueta_mm()
    lbl_actual = tk.Label(ventana, text=f"Configuración actual: {ancho_actual} x {alto_actual} mm", font=("Lato", 12))
    lbl_actual.pack(pady=10)
    
    # Combobox para seleccionar tamaño predefinido.
    lbl_combo = tk.Label(ventana, text="Seleccione un tamaño de etiqueta:", font=("Lato", 10))
    lbl_combo.pack(pady=5)
    combo = ttk.Combobox(ventana, values=opciones, state="readonly", font=("Lato", 10))
    combo.current(0)  # Seleccionar la primera opción por defecto
    combo.pack(pady=5)
    
    # Frame para entrada personalizada (aparece solo si se selecciona "Personalizado")
    frame_personalizado = tk.Frame(ventana)
    lbl_personalizado = tk.Label(frame_personalizado, text="Ingrese tamaño personalizado (mm):", font=("Lato", 10))
    lbl_personalizado.grid(row=0, column=0, columnspan=2, pady=5)
    lbl_ancho = tk.Label(frame_personalizado, text="Ancho:", font=("Lato", 10))
    lbl_ancho.grid(row=1, column=0, sticky="e", padx=5)
    entry_ancho = tk.Entry(frame_personalizado, font=("Lato", 10), width=10)
    entry_ancho.grid(row=1, column=1, padx=5)
    lbl_alto = tk.Label(frame_personalizado, text="Alto:", font=("Lato", 10))
    lbl_alto.grid(row=2, column=0, sticky="e", padx=5)
    entry_alto = tk.Entry(frame_personalizado, font=("Lato", 10), width=10)
    entry_alto.grid(row=2, column=1, padx=5)
    
    def actualizar_visibilidad(*args):
        if combo.get() == "Personalizado":
            frame_personalizado.pack(pady=5)
        else:
            frame_personalizado.forget()
    
    combo.bind("<<ComboboxSelected>>", actualizar_visibilidad)
    
    def guardar():
        if combo.get() == "Personalizado":
            try:
                nuevo_ancho = float(entry_ancho.get())
                nuevo_alto = float(entry_alto.get())
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
                return
        else:
            try:
                parts = combo.get().replace("mm", "").strip().split("x")
                nuevo_ancho = float(parts[0].strip())
                nuevo_alto = float(parts[1].strip())
            except Exception as e:
                messagebox.showerror("Error", f"Formato inválido en la opción seleccionada: {e}")
                return
        
        if guardar_config_etiqueta_mm(nuevo_ancho, nuevo_alto):
            messagebox.showinfo("Éxito", f"Nuevo tamaño de etiqueta configurado: {nuevo_ancho} x {nuevo_alto} mm", parent=ventana)
           
            lbl_actual.config(text=f"Configuración actual: {nuevo_ancho} x {nuevo_alto} mm")
        else:
            messagebox.showerror("Error", "No se pudo guardar la nueva configuración.",parent=ventana)
            
    btn_guardar = tk.Button(ventana, text="Guardar", command=guardar, font=("Lato", 10))
    btn_guardar.pack(pady=10)
    
    ventana.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    mostrar_ventana_config_etiqueta(root)