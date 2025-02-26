import tkinter as tk
import tkinter.font as tkFont
from tkinter import Menu, ttk, messagebox
from datetime import datetime
import json
import os
import pytz
import win32print
import random
from configuracion.windowsConfiWtiqueta import mostrar_ventana_config_etiqueta
from configuracion.material import cargar_materiales
import textwrap
# Configuraciones constantes
APP_DATA = os.getenv("APPDATA")
CONTROLADOR_FOLDER = os.path.join(APP_DATA, "EpsonDriver")
TIMEZONE = pytz.timezone("America/Mexico_City")
FONT_LCD = ("DS-Digital", 100, "bold")
FONT_LATO = ("Lato", 14)
FONT_LATO_LARGE = ("Lato", 30, "bold")
UPDATE_INTERVAL_MS = 100

# --- Funciones de peso aleatorio ---
def generar_peso_aleatorio() -> str:
    """Genera un peso aleatorio con formato 000.000"""
    return f"{random.randint(100, 999):03d}.{random.randint(0, 999):03d}"

# --- Funciones de Configuración de Etiqueta ---
def obtener_config_etiqueta() -> tuple[int, int]:
    
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
        ancho_mm = config.get("ancho", 76)
        alto_mm = config.get("alto", 51)
        dpi = 203
        ancho_dots = int((ancho_mm / 25.4) * dpi)
        alto_dots = int((alto_mm / 25.4) * dpi)
        return ancho_dots, alto_dots
    except Exception as e:
        print(f"Error al leer configuración de etiqueta: {e}")
        return 800, 600

import textwrap

import textwrap

def generar_zpl(descripcion: str, operador: str, origen: str, 
                destino: str, peso: str, fecha: str, hora: str,
                ancho: int, alto: int) -> str:
    """
    Genera ZPL para impresión con parámetros calculados automáticamente.
    
    Se usan 8 líneas en el orden lógico:
      1. "Descripción:" (etiqueta)
      2. Contenido de la descripción
      3. Operador: ...
      4. Origen: ...  (usa wrapping para textos largos)
      5. Destino: ... (usa wrapping para textos largos)
      6. Peso: ...
      7. Fecha: ...
      8. Hora: ...
    
    Si ancho < alto se considera que la etiqueta debe rotarse para imprimir en el lado mayor;
    en ese caso se intercambian las dimensiones para el cálculo, se añade el comando ^FWR y se
    invierte la forma de posicionar los campos (se intercambian las coordenadas en ^FO).
    Además, en modo rotado se muestra en consola cómo quedaría el código ZPL SIN rotación (simulado).
    """
    # Determinar si se debe rotar
    rotate = False
    if ancho < alto:
        rotate = True
        effective_width = alto    # La dimensión mayor se usa como "anchura efectiva"
        effective_height = ancho  # La dimensión menor se usa como "altura efectiva"
    else:
        effective_width = ancho
        effective_height = alto

    # Cantidad de líneas fijas: 8
    num_lines = 7
    # Se asigna el 70% del espacio de la dimensión efectiva menor para el contenido
    line_spacing = int((effective_height * 0.7) / num_lines)
    font_size = int(line_spacing * 0.80)
    # Márgenes:
    # En el modo no rotado: y_offset = 10% del alto; x_offset = 6% del ancho.
    # En modo rotado, usaremos el mismo valor para x_offset (que pasará a ser la coordenada fija) y y_offset (para iniciar la variable de posición).
    y_offset = int(effective_height * 0.07)
    x_offset = int(effective_width * 0.03)
    
    print(f"Configuración de etiqueta: ancho={ancho} dots, alto={alto} dots")
    if rotate:
        print(f"Rotación activada. Usando dimensiones efectivas: ancho={effective_width} dots, alto={effective_height} dots")
    print(f"Parámetros calculados: line_spacing={line_spacing}, font_size={font_size}, x_offset={x_offset}, y_offset={y_offset}")
    
    # Lista de campos en orden lógico (sin invertir el orden de la lista)
    fields = [
        f"Descripción: {descripcion}",
        f"Operador: {operador}",
        f"Origen: {origen}",
        f"Destino: {destino}",
        f"Peso: {peso} kg",
        f"Fecha: {fecha}",
        f"Hora: {hora}"
    ]
    
    # Se calculará el ancho del bloque para los campos con wrapping.
    # En modo no rotado, block_width = effective_width - 2*x_offset.
    # En modo rotado, el "ancho" para wrapping se tomará de la dimensión que se usa para la "altura" efectiva.
    if not rotate:
        block_width = effective_width - 2 * x_offset
    else:
        block_width = effective_width - 2 * x_offset
    # Estimar el número máximo de caracteres que caben en una línea (valor aproximado)
    max_chars = int(block_width / (font_size * 0.6))-4
    
    if not rotate:
        # Modo no rotado: impresión vertical
        zpl = "^XA\n"
        zpl += "^CI28\n"
        zpl += f"^CF0,{font_size}\n"
        
        current_y = y_offset
        for text in fields:
            # Para "Origen:" y "Destino:" aplicar wrapping
            if text.startswith("Origen:") or text.startswith("Destino:"):
                # Separamos el prefijo y el contenido
                if ":" in text:
                    prefix, content = text.split(":", 1)
                    prefix = prefix.strip() + ": "
                    content = content.strip()
                    wrapped_lines = textwrap.wrap(content, width=max_chars, break_long_words=True)
                    if wrapped_lines:
                        first_line = prefix + wrapped_lines[0]
                        zpl += f"^FO{x_offset},{current_y}^FD{first_line}^FS\n"
                        current_y += line_spacing
                        if len(wrapped_lines) > 1:
                            zpl += f"^FO{x_offset},{current_y}^FD{wrapped_lines[1]}^FS\n"
                            current_y += line_spacing
                        # Si el wrapped_lines tiene menos de 2 líneas, no se incrementa adicionalmente.
                    else:
                        zpl += f"^FO{x_offset},{current_y}^FD{text}^FS\n"
                        current_y += line_spacing
                else:
                    wrapped_lines = textwrap.wrap(text, width=max_chars, break_long_words=True)
                    for line in wrapped_lines[:2]:
                        zpl += f"^FO{x_offset},{current_y}^FD{line}^FS\n"
                        current_y += line_spacing
            else:
                zpl += f"^FO{x_offset},{current_y}^FD{text}^FS\n"
                current_y += line_spacing
        zpl += "^XZ"
        #print("Código ZPL generado (no rotado):")
        #print(zpl)
        # Además, para fines de comparación, se muestra en consola el código ZPL sin rotación.
        #print("Código ZPL generado SIN rotación (simulado):")
        #print(zpl)
        return zpl
    else:
        # Modo rotado: se usa ^FWR y se posicionan los campos horizontalmente.
        zpl = "^XA\n"
        zpl += "^FWR\n"  # Rota 90° en sentido horario
        zpl += "^CI28\n"
        zpl += f"^CF0,{font_size}\n"
        # En modo rotado, fijamos la coordenada vertical a x_offset (valor fijo).
        fixed_y = x_offset
        # Calculamos la posición inicial en el eje X: se inicia en y_offset + (num_lines - 1) * line_spacing
        # Agregamos un extra para empujar el primer campo hacia la derecha.
        extra_offset = int(effective_height * 0.15)  # Ajustable según lo deseado.
        start_x = y_offset + (num_lines - 1) * line_spacing + extra_offset
        
        for text in fields:
            if text.startswith("Origen:") or text.startswith("Destino:"):
                if ":" in text:
                    prefix, content = text.split(":", 1)
                    prefix = prefix.strip() + ": "
                    content = content.strip()
                    wrapped_lines = textwrap.wrap(content, width=max_chars, break_long_words=True)
                    if wrapped_lines:
                        first_line = prefix + wrapped_lines[0]
                        zpl += f"^FO{start_x},{fixed_y}^FD{first_line}^FS\n"
                        start_x -= line_spacing
                        if len(wrapped_lines) > 1:
                            zpl += f"^FO{start_x},{fixed_y}^FD{wrapped_lines[1]}^FS\n"
                            start_x -= line_spacing
                    else:
                        zpl += f"^FO{start_x},{fixed_y}^FD{text}^FS\n"
                        start_x -= line_spacing
                else:
                    wrapped_lines = textwrap.wrap(text, width=max_chars, break_long_words=True)
                    for line in wrapped_lines[:2]:
                        zpl += f"^FO{start_x},{fixed_y}^FD{line}^FS\n"
                        start_x -= line_spacing
            else:
                zpl += f"^FO{start_x},{fixed_y}^FD{text}^FS\n"
                start_x -= line_spacing
        
        zpl += "^XZ"
        
        #print("Código ZPL generado (rotado):")
        #print(zpl)
        return zpl


def imprimir_etiqueta(descripcion: str, operador: str, origen: str, 
                      destino: str, peso: str, fecha: str, hora: str) -> None:
    ancho, alto = obtener_config_etiqueta()
    zpl_comando = generar_zpl(descripcion, operador, origen, destino, peso, fecha, hora, ancho, alto)
    # Imprimir en consola el código ZPL que se va a enviar
    print("Código ZPL a enviar a la impresora (RAW):")
    print(zpl_comando)
    try:
        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        hjob = win32print.StartDocPrinter(hprinter, 1, ("Etiqueta", None, "RAW"))
        win32print.StartPagePrinter(hprinter)
        win32print.WritePrinter(hprinter, zpl_comando.encode("utf-8"))
        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
        win32print.ClosePrinter(hprinter)
    except Exception as e:
        messagebox.showerror("Error de impresión", f"No se pudo imprimir: {str(e)}")

# --- Interfaz Gráfica ---
def crear_interfaz_grafica(opciones_descripcion: list) -> tuple[tk.Tk, tk.Label]:
    app = tk.Tk()
    app.title("Sistema de Impresión de Etiquetas")
    app.configure(background='white')
    app.geometry("800x500")

    # Frame principal
    main_frame = tk.Frame(app, bg="white")
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Sección de fecha y hora
    ahora = datetime.now(TIMEZONE)
    fecha_hora_frame = tk.Frame(main_frame, bg="white")
    fecha_hora_frame.pack(fill="x")
    
    lbl_fecha = tk.Label(fecha_hora_frame, text=f"Fecha: {ahora.strftime('%Y-%m-%d')}", 
                        font=FONT_LATO, bg="white")
    lbl_fecha.pack(side="left")
    
    lbl_hora = tk.Label(fecha_hora_frame, text=f"Hora: {ahora.strftime('%H:%M:%S')}", 
                       font=FONT_LATO, bg="white")
    lbl_hora.pack(side="right")

    # Campos de entrada
    form_frame = tk.Frame(main_frame, bg="white")
    form_frame.pack(pady=20, fill="x")
    
    campos = [
        ("Descripción del Material:", ttk.Combobox(form_frame, values=opciones_descripcion, 
                                                 font=FONT_LATO, width=30, state="readonly")),
        ("Operador:", tk.Entry(form_frame, font=FONT_LATO, width=35)),
        ("Origen:", tk.Entry(form_frame, font=FONT_LATO, width=35)),
        ("Destino:", tk.Entry(form_frame, font=FONT_LATO, width=35)),
    ]

    for idx, (texto, widget) in enumerate(campos):
        lbl = tk.Label(form_frame, text=texto, font=FONT_LATO, bg="white")
        lbl.grid(row=idx, column=0, sticky="w", pady=5, padx=5)
        widget.grid(row=idx, column=1, pady=5, padx=5, sticky="ew")
    
    campos[0][1].set(opciones_descripcion[0])

    # Botones
    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(pady=20)
    
    btn_imprimir = tk.Button(button_frame, text="Imprimir Etiqueta", font=FONT_LATO,
                           command=lambda: procesar_impresion(
                               campos[0][1].get(),
                               campos[1][1].get(),
                               campos[2][1].get(),
                               campos[3][1].get(),
                               main_frame),
                           bg="#4CAF50", fg="white", width=20)
    btn_imprimir.pack(side="left", padx=10)

    btn_limpiar = tk.Button(button_frame, text="Limpiar Campos", font=FONT_LATO,
                          command=lambda: limpiar_campos(campos),
                          bg="#f44336", fg="white", width=15)
    btn_limpiar.pack(side="left", padx=10)

    # Menú de configuración
    menu_bar = Menu(app)
    menu_config = Menu(menu_bar, tearoff=0)
    menu_config.add_command(label="Tamaño de Etiqueta", 
                          command=lambda: mostrar_ventana_config_etiqueta(app))
    menu_bar.add_cascade(label="Configuraciones", menu=menu_config)
    app.config(menu=menu_bar)

    return app, lbl_hora

def limpiar_campos(campos):
    for _, widget in campos:
        if isinstance(widget, ttk.Combobox):
            widget.set(widget['values'][0])
        else:
            widget.delete(0, tk.END)

def procesar_impresion(descripcion, operador, origen, destino, parent):
    peso = generar_peso_aleatorio()
    ahora = datetime.now(TIMEZONE)
    
    imprimir_etiqueta(
        descripcion=descripcion,
        operador=operador,
        origen=origen,
        destino=destino,
        peso=peso,
        fecha=ahora.strftime("%Y-%m-%d"),
        hora=ahora.strftime("%H:%M:%S")
    )
    

if __name__ == "__main__":
    opciones_materiales = cargar_materiales()
    app, _ = crear_interfaz_grafica(opciones_materiales)
    app.mainloop()