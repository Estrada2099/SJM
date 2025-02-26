import tkinter as tk
from tkinter import messagebox
import json
import os

# Determinar la ruta de APPDATA y establecer la ruta para materiales.json
appdata_path = os.environ.get('APPDATA')
if not appdata_path:
    messagebox.showerror("Error", "No se pudo determinar la ruta de APPDATA.")
    raise EnvironmentError("APPDATA no está definido.")

# Definir la ruta completa dentro de APPDATA/ControladorEpson/materiales.json
carpeta_controlador = os.path.join(appdata_path, "EpsonDriver")
ruta_materiales = os.path.join(carpeta_controlador, "materiales.json")

# Asegurarse de que la carpeta ControladorEpson existe
if not os.path.exists(carpeta_controlador):
    try:
        os.makedirs(carpeta_controlador)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear la carpeta ControladorEpson: {str(e)}")
        raise

# Función para cargar o crear materiales por defecto
def cargar_materiales():
    if not os.path.exists(ruta_materiales):
        # Crear un archivo JSON con materiales predefinidos si no existe
        materiales_iniciales = {
            "materiales": [
                "Carton Nacional",
                "Carton (Celanes)",
                "Empaque",
                "Playo",
                "Bolsa de Plastico",
                "Lamina Negra",
                "Bolsa de Carton"
            ]
        }
        try:
            with open(ruta_materiales, "w", encoding="utf-8") as archivo:
                json.dump(materiales_iniciales, archivo, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el archivo materiales.json: {str(e)}")
            raise
    # Leer y devolver los materiales desde el archivo
    try:
        with open(ruta_materiales, "r", encoding="utf-8") as archivo:
            return json.load(archivo)["materiales"]
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo materiales.json: {str(e)}")
        return []

# Función para guardar un nuevo material en el JSON
def guardar_material(nuevo_material, ventana):
    try:
        # Leer materiales actuales
        with open(ruta_materiales, "r", encoding="utf-8") as archivo:
            data = json.load(archivo)

        # Verificar que no exista ya el material
        if nuevo_material in data["materiales"]:
            messagebox.showerror("Error", "El material ya existe.", parent=ventana)
            return False

        # Agregar el nuevo material
        data["materiales"].append(nuevo_material)
        with open(ruta_materiales, "w", encoding="utf-8") as archivo:
            json.dump(data, archivo, indent=4)
            
        messagebox.showinfo("Éxito", "Material agregado correctamente.", parent=ventana)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar el material: {str(e)}", parent=ventana)
        return False

# Función para actualizar el archivo JSON con los materiales
def actualizar_materiales(nuevos_materiales):
    try:
        data = {"materiales": nuevos_materiales}
        with open(ruta_materiales, "w", encoding="utf-8") as archivo:
            json.dump(data, archivo, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el archivo materiales.json: {str(e)}")

# Función para abrir la ventana CRUD de materiales con scroll
def ventana_material_crud(app):
    # Crear la ventana de materiales
    ventana = tk.Toplevel(app)
    ventana.title("Gestión de Materiales")
    ventana.geometry("500x700")
    ventana.resizable(False, False)
    
    def guardar_nuevo_material():
        nuevo_material = entry_material.get().strip()
        if not nuevo_material:
            messagebox.showerror("Error", "El material no puede estar vacío.", parent=ventana)
            return
        
        if guardar_material(nuevo_material, ventana):
            entry_material.delete(0, tk.END)  # Limpiar el campo después de guardar
            # Actualizar la lista de materiales desde el archivo
            global materiales
            materiales = cargar_materiales()  # Recargar desde el archivo
            recargar_materiales()  # Actualizar la interfaz

    def eliminar_material(material):
        # Mostrar diálogo de confirmación para eliminar
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el material '{material}'?",
            parent=ventana
        )
        
        if confirmar:
            # Recargar la lista actual desde el archivo antes de modificar
            global materiales
            materiales = cargar_materiales()
            if material in materiales:
                materiales.remove(material)
                actualizar_materiales(materiales)
                messagebox.showinfo(
                    "Éxito",
                    "Material eliminado correctamente.\nPara ver los cambios reflejados, reinicie la aplicación.",
                    parent=ventana
                )
                recargar_materiales()
            else:
                messagebox.showerror(
                    "Error",
                    "El material no se encuentra en la lista.",
                    parent=ventana
                )

    def editar_material(material, entry, btn_editar):
        # Si el botón dice "Editar", activamos la edición
        if btn_editar["text"] == "Editar":
            entry.config(state="normal")
            btn_editar.config(text="Actualizar", bg="green")
        else:  # Si dice "Actualizar", pedimos confirmación
            nuevo_nombre = entry.get().strip()
            if not nuevo_nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío.", parent=ventana)
                return
                
            # Recargar la lista actual desde el archivo antes de verificar
            global materiales
            materiales = cargar_materiales()
            
            if nuevo_nombre != material and nuevo_nombre in materiales:
                messagebox.showerror("Error", "El material ya existe.", parent=ventana)
                return
                
            # Mostrar diálogo de confirmación
            confirmar = messagebox.askyesno(
                "Confirmar actualización",
                f"¿Está seguro que desea actualizar este material de '{material}' a '{nuevo_nombre}'?",
                parent=ventana
            )
            
            if confirmar:
                if material in materiales:
                    index = materiales.index(material)
                    materiales[index] = nuevo_nombre
                    actualizar_materiales(materiales)
                    entry.config(state="readonly")
                    btn_editar.config(text="Editar", bg="orange")
                    messagebox.showinfo(
                        "Éxito",
                        "Material actualizado correctamente.\nPara ver los cambios reflejados, reinicie la aplicación.",
                        parent=ventana
                    )
                    recargar_materiales()
                else:
                    messagebox.showerror(
                        "Error",
                        "El material no se encuentra en la lista.",
                        parent=ventana
                    )
            else:
                # Si no confirma, volvemos al estado anterior
                entry.delete(0, tk.END)
                entry.insert(0, material)
                entry.config(state="readonly")
                btn_editar.config(text="Editar", bg="orange")

    def recargar_materiales():
        # Limpiar el frame de materiales
        for widget in frame_materiales.winfo_children():
            widget.destroy()

        # Asegurarse de tener la lista más actualizada
        global materiales
        materiales = cargar_materiales()

        for material in materiales:
            material_frame = tk.Frame(frame_materiales)
            material_frame.pack(fill="x", padx=10, pady=5)

            entry_nombre = tk.Entry(material_frame, font=("Lato", 12))
            entry_nombre.insert(0, material)
            entry_nombre.config(state="readonly")
            entry_nombre.pack(side="left", fill="x", expand=True, padx=5)

            btn_editar = tk.Button(
                material_frame,
                text="Editar",
                font=("Lato", 12),
                bg="orange",
                fg="white",
                width=10,
                command=lambda m=material, e=entry_nombre, b=None: editar_material(m, e, b)
            )
            btn_editar.pack(side="left", padx=5)
            btn_editar.configure(command=lambda m=material, e=entry_nombre, b=btn_editar: editar_material(m, e, b))

            btn_eliminar = tk.Button(
                material_frame,
                text="Eliminar",
                font=("Lato", 12),
                bg="red",
                fg="white",
                command=lambda m=material: eliminar_material(m)
            )
            btn_eliminar.pack(side="left", padx=5)

    # Contenedor principal con scrollbar
    contenedor = tk.Frame(ventana)
    contenedor.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(contenedor)
    scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Etiqueta y entrada para un nuevo material
    tk.Label(scrollable_frame, text="Nuevo Material:", font=("Lato", 14)).pack(pady=10)
    entry_material = tk.Entry(scrollable_frame, font=("Lato", 14), width=30)
    entry_material.pack(pady=10)

    # Botón para guardar el material
    btn_guardar = tk.Button(scrollable_frame, text="Guardar", font=("Lato", 14), bg="blue", fg="white", command=guardar_nuevo_material)
    btn_guardar.pack(pady=10)

    # Frame para la lista de materiales con opciones de editar/eliminar
    frame_materiales = tk.Frame(scrollable_frame)
    frame_materiales.pack(fill="both", expand=True)

    # Cargar materiales existentes
    materiales = cargar_materiales()
    recargar_materiales()


