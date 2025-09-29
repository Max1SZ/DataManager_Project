# Ventana principal
# ======================
# main.py
# ======================

import tkinter as tk
from tkinter import ttk, filedialog
from functions import *  # importamos nuestras funciones

# ------------------
# Ventana principal
# ------------------
root = tk.Tk()
root.title("DataManager v3")
root.geometry("900x600")

# Frame dinámico
contenedor = tk.Frame(root)
contenedor.pack(fill="both", expand=True, padx=10, pady=10)

# ------------------
# Helpers
# ------------------
def limpiar_frame():
    for widget in contenedor.winfo_children():
        widget.destroy()

def mostrar_dataframe(df, titulo="Resultado"):
    """Muestra un DataFrame en un Treeview dentro del contenedor."""
    limpiar_frame()
    tk.Label(contenedor, text=titulo, font=("Arial", 14, "bold")).pack(pady=10)

    frame_tabla = tk.Frame(contenedor)
    frame_tabla.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame_tabla, columns=list(df.columns), show="headings")
    tree.pack(fill="both", expand=True)

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

# ------------------
# Pantallas
# ------------------
def pantalla_inicio():
    limpiar_frame()
    tk.Label(contenedor, text="🏠 Bienvenido al gestor de datasets",
             font=("Arial", 18, "bold")).pack(pady=20)

def pantalla_cargar():
    rutas = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
    if rutas:
        cargar_csv(rutas)

def pantalla_guardar():
    if not csvs:
        return
    guardar_todos()

def pantalla_ranking():
    df = ranking_clientes()
    if df is not None:
        mostrar_dataframe(df, "Ranking clientes")

# ------------------
# Menú superior
# ------------------
menu = tk.Menu(root)
root.config(menu=menu)

menu_principal = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Menú", menu=menu_principal)

menu_principal.add_command(label="Inicio", command=pantalla_inicio)
menu_principal.add_command(label="Cargar Dataset", command=pantalla_cargar)
menu_principal.add_command(label="Guardar", command=pantalla_guardar)
menu_principal.add_command(label="Ranking clientes", command=pantalla_ranking)
menu_principal.add_separator()
menu_principal.add_command(label="Salir", command=root.quit)

# ------------------
# Iniciar app
# ------------------
pantalla_inicio()
root.mainloop()
