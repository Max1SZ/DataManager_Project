# functions.py
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# =====================
# CONFIGURACIÓN GLOBAL
# =====================
engine = sqlalchemy.create_engine("mysql+pymysql://root:@localhost/empresa_ca")
csvs = {}   # {nombre_csv: (DataFrame, ruta)}
tree = None # el Treeview se asigna desde main.py

def set_treeview(t):  
    """Asignar el Treeview desde main.py"""
    global tree
    tree = t
    

# =====================
# FUNCIONES BÁSICAS
# =====================
def cargar_csv():
    rutas = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
    for ruta in rutas:
        try:
            df = pd.read_csv(ruta)
            nombre = ruta.split("/")[-1].replace(".csv", "")
            csvs[nombre] = (df, ruta)
            messagebox.showinfo("Éxito", f"{nombre} cargado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar {ruta}: {e}")

def guardar_todos():
    for nombre, (df, ruta) in csvs.items():
        df.to_csv(ruta, index=False)
    messagebox.showinfo("Éxito", "Todos los CSVs fueron guardados.")

def subir_sql(nombre=None):
    if not csvs:
        messagebox.showwarning("Atención", "No hay CSVs cargados.")
        return
    if nombre: # subir solo uno
        dfs = {nombre: csvs[nombre]}
    else: # subir todos
        dfs = csvs
    for n, (df, _) in dfs.items():
        try:
            df.to_sql(n, con=engine, if_exists='replace', index=False)
            messagebox.showinfo("Éxito", f"{n} subido a SQL")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo subir {n}: {e}")

def mostrar_dataframe(df, titulo="Resultado"):
    if tree is None: return
    tree.delete(*tree.get_children())
    tree["columns"] = list(df.columns)
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

# =====================
# REPORTES
# =====================
def ranking_clientes():
    if "clientes" not in csvs or "facturas_enc" not in csvs:
        messagebox.showwarning("Atención", "Carga clientes y facturas_enc")
        return
    clientes, _ = csvs["clientes"]
    facturas, _ = csvs["facturas_enc"]
    merged = pd.merge(facturas, clientes, on="id_cliente")
    df = merged.groupby("nombre")["total"].sum().reset_index()
    df = df.sort_values(by="total", ascending=False).head(10)
    mostrar_dataframe(df, "Ranking clientes")

def ticket_promedio():
    if "clientes" not in csvs or "facturas_enc" not in csvs:
        messagebox.showwarning("Atención", "Carga clientes y facturas_enc")
        return
    clientes, _ = csvs["clientes"]
    facturas, _ = csvs["facturas_enc"]
    merged = pd.merge(facturas, clientes, on="id_cliente")
    df = merged.groupby("nombre")["total"].mean().reset_index()
    df.rename(columns={"total": "ticket_promedio"}, inplace=True)
    mostrar_dataframe(df.sort_values(by="ticket_promedio", ascending=False).head(10))

def facturas_altas():
    if "facturas_enc" not in csvs:
        messagebox.showwarning("Atención", "Carga facturas_enc")
        return
    facturas, _ = csvs["facturas_enc"]
    df = facturas.sort_values(by="total", ascending=False).head(10)
    mostrar_dataframe(df, "Facturas más altas")

def ventas_por_mes():
    if "facturas_enc" not in csvs:
        messagebox.showwarning("Atención", "Carga facturas_enc")
        return
    facturas, _ = csvs["facturas_enc"]
    if facturas.empty or "fecha" not in facturas.columns or "total" not in facturas.columns:
        messagebox.showerror("Error", "El archivo facturas_enc no tiene datos válidos.")
        return
    facturas["fecha"] = pd.to_datetime(facturas["fecha"], errors="coerce")
    df = facturas.groupby(facturas["fecha"].dt.to_period("M"))["total"].sum().reset_index()
    df.rename(columns={"fecha": "mes"}, inplace=True)
    mostrar_dataframe(df, "Ventas por mes")
    return df

def producto_mas_vendido():
    if "facturas_det" not in csvs or "productos" not in csvs:
        messagebox.showwarning("Atención", "Carga facturas_det y productos")
        return
    fdet, _ = csvs["facturas_det"]
    prods, _ = csvs["productos"]
    df = fdet.groupby("id_producto")["cantidad"].sum().reset_index()
    df = pd.merge(df, prods, on="id_producto")
    mostrar_dataframe(df.sort_values(by="cantidad", ascending=False).head(5),
                      "Productos más vendidos")

def ventas_por_rubro():
    if "facturas_det" not in csvs or "productos" not in csvs or "rubros" not in csvs:
        messagebox.showwarning("Atención", "Carga facturas_det, productos y rubros")
        return
    fdet, _ = csvs["facturas_det"]
    prods, _ = csvs["productos"]
    rubros, _ = csvs["rubros"]
    df = pd.merge(fdet, prods, on="id_producto")
    df = pd.merge(df, rubros, on="id_rubro")
    df = df.groupby("nombre")["cantidad"].sum().reset_index()
    mostrar_dataframe(df.sort_values(by="cantidad", ascending=False),
                      "Ventas por rubro")

def grafico_ventas():
    df_mes = ventas_por_mes()
    if df_mes is None or df_mes.empty:
        messagebox.showwarning("Atención", "No hay datos para graficar.")
        return
    df_mes.set_index("mes")["total"].plot(kind="bar", figsize=(8, 4))
    plt.title("Ventas mensuales")
    plt.xlabel("Mes")
    plt.ylabel("Total")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def top_productos_facturacion():
    if "facturas_det" not in csvs or "productos" not in csvs:
        messagebox.showwarning("Atención", "Carga facturas_det y productos")
        return
    fdet, _ = csvs["facturas_det"]
    prods, _ = csvs["productos"]
    df = pd.merge(fdet, prods, on="id_producto")
    df["importe"] = df["cantidad"] * df["precio_unitario"]
    df = df.groupby("nombre")["importe"].sum().reset_index()
    mostrar_dataframe(df.sort_values(by="importe", ascending=False).head(10),
                      "Top productos por facturación")
