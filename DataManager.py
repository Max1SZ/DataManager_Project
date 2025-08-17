import pandas as pd
import sqlalchemy
#importamos librerias (asegurate de descargarlas)

# Configuración de la conexión con MySQL
'''
*root es el usuario.
*: es separador entre usuario y contraseña.
*@localhost es host (donde corre MySQL, en tu caso tu propia PC).
*empresa_ca la base de datos. 
*Como no hay contraseña, después de root: se deja vacío. sino iria la que haya puesto uno.
*CAMBIAR A PREFERENCIA
'''

engine = sqlalchemy.create_engine("mysql+pymysql://root:@localhost/empresa_ca")

# Lista donde vamos a guardar los datos
registros = []

# Menú simple
while True:
    print("\n--- MENÚ ---")
    print("1. Agregar empleado")
    print("2. Guardar en CSV")
    print("3. Subir CSV a la base de datos")
    print("4. Salir")

    opcion = input("Elige una opción: ")

    if opcion == "1":
        nombre = input("Nombre: ")
        edad = int(input("Edad: "))
        labor = input("Labor: ")
        registros.append([nombre, edad, labor])

    elif opcion == "2":
        # Crear DataFrame y exportar a CSV
        df = pd.DataFrame(registros, columns=["nombre", "edad", "labor"])
        df.to_csv("empleados.csv", index=False)
        print("✅ Datos guardados en empleados.csv")

    elif opcion == "3":
        try:
            # Leemos el CSV
            df = pd.read_csv("empleados.csv")

            # Subimos a la base de datos
            df.to_sql("empleados", engine, if_exists="append", index=False)

            print("✅ CSV enviado a la base de datos")
        except Exception as e:
            print("❌ Error al subir datos:", e)

    elif opcion == "4":
        print("👋 Saliendo del programa...")
        break

    else:
        print("Opción no válida")
