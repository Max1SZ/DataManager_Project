'''
-----------------
DataManager_v2c 
El codigo lo que hara sera:
* Permitir al usuario cargar uno o varios archivos CSV.
* Mostrar un menú para agregar, modificar o eliminar filas en los DataFrames cargados.
* Permitir guardar los cambios en los archivos CSV originales.
* Subir los datos modificados a una base de datos SQL.
* Utiliza pandas para manejar los datos y SQLAlchemy para la conexión con la base de datos.
-----------------'''

import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt

# Conexión a la base de datos (ajusta los datos según tu entorno)
engine = sqlalchemy.create_engine("mysql+pymysql://root:@localhost/empresa_ca")

# Diccionario para almacenar los DataFrames y sus rutas
csvs = {}  # nombre_csv : (df, ruta)

#-----------------
# helper: checar si los csvs necesarios existen
def get_csvs_requeridos(*rutas_o_nombres):
    dfs = []
    for entrada in rutas_o_nombres:
        nombre = entrada.split("/")[-1].replace(".csv", "") if ".csv" in entrada else entrada
        if nombre not in csvs:
            print(f"❌ Falta el CSV: {nombre}")
            return None
        dfs.append(csvs[nombre][0])
    return dfs
#-----------------
# Cargar uno o varios CSVs
def cargar_csv():
    rutas = input("Rutas de los CSV (separadas por coma): ").split(",")
    for ruta in rutas:
        ruta = ruta.strip()
        if ruta == "" or not ruta.endswith(".csv"):
            print(f"Ruta inválida: {ruta}")
            continue
        try:
            df = pd.read_csv(ruta)
            nombre = ruta.split("/")[-1].replace(".csv", "")
            csvs[nombre] = (df, ruta)
            print(f"✅ {nombre} cargado.")
        except Exception as e:
            print(f"Error al cargar {ruta}: {e}")
#-----------------
# Mostrar un CSV
def check_csv():
    if not csvs:
        print("No hay CSVs cargados.")
        return
    print("Archivos disponibles:")
    for i, nombre in enumerate(csvs):
        print(f"{i+1}. {nombre}")
    try:
        idx = int(input("Elige el número del CSV: ")) - 1
        nombre = list(csvs.keys())[idx]
        df, _ = csvs[nombre]
        print(df)
    except (ValueError, IndexError):
        print("Opción inválida.")
#-----------------    
# Modificar un CSV
def modify_csv():
    if not csvs:
        print("No hay CSVs cargados.")
        return
    print("Archivos disponibles:")
    for i, nombre in enumerate(csvs):
        print(f"{i+1}. {nombre}")
    try:
        idx = int(input("Elige el número del CSV: ")) - 1
        nombre = list(csvs.keys())[idx]
        df, ruta = csvs[nombre]
        print("Columnas disponibles:", list(df.columns)) # muestra las columnas del csv
        fila = int(input("Número de fila a modificar: "))
        if fila < 0 or fila >= len(df): # checa que la fila exista
            print("Fila inválida.")
            return
        columna = input("Nombre de la columna a modificar: ").strip()
        if columna not in df.columns:
            print("Columna inválida.")
            return
        nuevo_valor = input("Nuevo valor: ")
        df.at[fila, columna] = nuevo_valor
        df.to_csv(ruta, index=False)
        print("CSV modificado y guardado.")
        csvs[nombre] = (df, ruta) # actualiza el diccionario
    except (ValueError, IndexError):
        print("Entrada inválida.")
#-----------------    
# Guardar cambios en todos los CSVs
def save_all_csvs():
    for nombre, (df, ruta) in csvs.items():
        df.to_csv(ruta, index=False)
        print(f"Cambios guardados en {ruta}")
#-----------------    
# Subir datos a SQL
def upload_to_sql():
    if not csvs:
        print("No hay CSVs cargados.")
        return
    for nombre, (df, _) in csvs.items():
        try:
            df.to_sql(nombre, con=engine, if_exists='replace', index=False)
            print(f"Datos de {nombre} subidos a SQL.")
        except Exception as e:
            print(f"Error al subir {nombre} a SQL: {e}")

#-----------------
# Unificar más de dos tablas en cadena
def unify_tables():
    if len(csvs) < 2:
        print("Necesitas al menos 2 CSVs cargados.")
        return

    print("Archivos disponibles:")
    for i, nombre in enumerate(csvs):
        print(f"{i+1}. {nombre}")

    try:
        indices = input("Elige los números de los CSVs a unir (separados por coma, ej: 1,2,3): ")
        indices = [int(x.strip()) - 1 for x in indices.split(",") if x.strip().isdigit()]
        if len(indices) < 2:
            print("Debes seleccionar al menos 2 CSVs.")
            return

        # Tomar el primero como base
        nombre_base = list(csvs.keys())[indices[0]]
        merged_df, _ = csvs[nombre_base]

        # Para unir los demás en cadena
        for idx in indices[1:]:
            nombre = list(csvs.keys())[idx]
            df, _ = csvs[nombre]

            print(f"\nUniendo {nombre_base} con {nombre}...")
            print("Columnas disponibles en la tabla base:", list(merged_df.columns))
            print("Columnas disponibles en", nombre, ":", list(df.columns))
            key = input("Columna en común para unir: ").strip()

            merged_df = pd.merge(merged_df, df, on=key, how="left")
            nombre_base += f"_{nombre}"  # ir concatenando nombres para el resultado

        print("\n Resultado de la unión en cadena (primeras filas):")
        print(merged_df.head())

        # Guardar opcionalmente
        guardar = input("¿Quieres guardar el resultado como un nuevo CSV? (s/n): ").strip().lower()
        if guardar == "s":
            nuevo_nombre = f"{nombre_base}_merge"
            csvs[nuevo_nombre] = (merged_df, f"{nuevo_nombre}.csv")
            merged_df.to_csv(f"{nuevo_nombre}.csv", index=False)
            print(f"\n Unión en cadena guardada como {nuevo_nombre}.csv y disponible en memoria.")
        else:
            print("\n Unión no guardada, solo mostrada en pantalla.")

    except Exception as e:
        print(f"Error al unir tablas: {e}")
#-----------------
# Función que une ventas, facturas y clientes como en el pdf. 
# Aca en vez de fact_enc es el ambos por que no hay id_producto en el encabezado pero se necesita para lo otro con clientes
def vc():
    dfs = get_csvs_requeridos("clientes", "facturas_det", "ventas","facturas_enc")
    if dfs is None:
        print("❌ No se pudieron cargar los DataFrames necesarios.")
        return None
    clientes, facturas_det, ventas, facturas_enc = dfs
    ventas_clientes = pd.merge(ventas, facturas_det) 
    ventas_clientes = pd.merge(ventas_clientes, facturas_enc, on="id_sucursal", how="left")
    ventas_clientes = pd.merge(ventas_clientes, clientes, on="id_cliente", how="left")
    return ventas_clientes
#-----------------
# Ranking de clientes por total comprado
def ranking():
    ventas_clientes = vc()
    if ventas_clientes is None:
        print("No se pudo generar el DataFrame combinado.")
        return
    df_ranking = ventas_clientes.groupby('nombre')['total'].sum().reset_index()
    df_ranking = df_ranking.sort_values(by='total', ascending=False)
    print("Top 10 clientes por total comprado:")
    print(df_ranking.head(10))
    return df_ranking
#-----------------
# Ticket promedio por cliente
def ticket_promedio():
    ventas_clientes = vc()
    ticket_promedio = ventas_clientes.groupby('nombre')['total'].mean().reset_index()
    ticket_promedio.rename(columns={'total': 'ticket_promedio'}, inplace=True)
    print(ticket_promedio.sort_values(by='ticket_promedio', ascending=False).head(10))
    return ticket_promedio
#-----------------
# Ventas por mes
def ventas_por_mes():
    ventas_clientes = vc()
    ventas_clientes['fecha_y'] = pd.to_datetime(ventas_clientes['fecha_y'])
    ventas_por_mes = ventas_clientes.groupby(ventas_clientes['fecha_y'].dt.to_period('M'))['total'].sum().reset_index()
    print(ventas_por_mes)
    return ventas_por_mes
#-----------------
# Facturas más altas
def top_facturas():
    ventas_clientes = vc()
    top_facturas = ventas_clientes.sort_values(by='total', ascending=False).head(10)
    top_facturas = top_facturas[['id_factura', 'fecha_y', 'nombre', 'total']]
    print(top_facturas)
    return top_facturas
#-----------------
# Producto más vendido en cantidad
def top_prods():
    dfs = get_csvs_requeridos("facturas_det", "productos")
    if not dfs: return
    facturas_det, productos = dfs
    print("Columnas en facturas_det:", facturas_det.columns.tolist())
    if 'id_producto' not in facturas_det.columns or 'cantidad' not in facturas_det.columns:
        print("❌ Columnas necesarias no están presentes en facturas_det.")
        return
    top_prods = facturas_det.groupby('id_producto')['cantidad'].sum().reset_index()
    top_prods = pd.merge(top_prods, productos, on='id_producto')
    print(top_prods.sort_values(by='cantidad', ascending=False).head(1))
    return top_prods
#-----------------
# Ventas totales por rubro
def det_rubro():
    dfs = get_csvs_requeridos("C:/Users/estudiante/Desktop/TareasPYTHON/2025/facturas_det.csv", 
                              "C:/Users/estudiante/Desktop/TareasPYTHON/2025/productos.csv")
    if not dfs: return
    rubros = pd.read_csv("C:/Users/estudiante/Desktop/TareasPYTHON/2025/rubros.csv")
    facturas_det, productos = dfs
    det_rubro = pd.merge(facturas_det, productos, on='id_producto')
    det_rubro = pd.merge(det_rubro,rubros, on='id_rubro') 
    det_rubro = det_rubro.groupby('nombre')['cantidad'].sum().reset_index()
    print(det_rubro.sort_values(by='cantidad', ascending=False))
    return det_rubro
#-----------------
# Gráfico de ventas mensuales
def grafico_ventas_mensuales():
    df_ventas = ventas_por_mes()  # ← ahora no hay conflicto
    df_ventas.set_index('fecha_y', inplace=True)
    df_ventas['total'].plot(kind='bar', figsize=(10,5))
    plt.title('Ventas Mensuales')
    plt.xlabel('Mes')
    plt.ylabel('Total Ventas')
    plt.tight_layout()
    plt.show()
#-----------------
# Top productos por facturación
def fac_prod():
    dfs = get_csvs_requeridos("C:/Users/estudiante/Desktop/TareasPYTHON/2025/facturas_det.csv", 
                              "C:/Users/estudiante/Desktop/TareasPYTHON/2025/productos.csv")
    if not dfs: return
    facturas_det, productos = dfs
    top_prod = pd.merge(facturas_det, productos, on='id_producto')
    top_prod['importe'] = top_prod['cantidad'] * top_prod['precio_unitario'] 
    ranking_prod = top_prod.groupby('descripcion')['importe'].sum().reset_index()
    print(ranking_prod.sort_values(by='importe', ascending=False).head(10))
    return ranking_prod
#-----------------
# Menú simple
while True:
    print("\n--- MENÚ ---")
    print("1. Insertar uno o varios CSVs")
    print("2. Checar un CSV")
    print("3. Modificar un CSV")
    print("4. Guardar todos los cambios")
    print("5. Subir datos a SQL")
    print("6. Unificar tablas")
    print("7. Reportes")
    print("0. Salir")

    opcion = input("Elige una opción: ")
    
    if opcion == "1":
        cargar_csv()
    elif opcion == "2":
        check_csv()
    elif opcion == "3":
        modify_csv()
    elif opcion == "4":
        save_all_csvs()
    elif opcion == "5":
        upload_to_sql()
    elif opcion == "6":
        unify_tables()
    elif opcion == "7":
        print("\n--- REPORTES ---")
        print("1. Ranking clientes")
        print("2. Ticket promedio")
        print("3. Facturas más altas")
        print("4. Ventas por mes")
        print("5. Producto más vendido")
        print("6. Ventas por rubro")
        print("7. Gráfico ventas mensuales")
        print("8. Top productos facturación")
        sub = input("Elige reporte: ")
        if sub == "1": ranking()
        elif sub == "2": ticket_promedio()
        elif sub == "3": top_facturas()
        elif sub == "4": ventas_por_mes()
        elif sub == "5": top_prods()
        elif sub == "6": det_rubro()
        elif sub == "7": grafico_ventas_mensuales()
        elif sub == "8": fac_prod()
        else: print("Opción inválida")
    elif opcion == "0":
        print("👋 Saliendo del programa...")
        break
    else:
        print("Opción no válida")