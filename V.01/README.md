IMPORTANTE:
*Importar el sql a tu phpmyadmin 
*modificar parte del codigo en la parte donde habla del usuario, vas a verlo en comentarios. 

Resumen:
Lo que hace el .py es basicamente darte 3 opciones: 

1. introducir datos segun la clasificacion que tendrian (y concuerde con la base de datos)
   
2. volver esos datos en un csv mediante la libreria pandas y dejandolos en la misma direccion donde se situe el .py

3. el codigo mediante las librerias sqlalchemy y pymysql agarra el csv
  y lo sube a la base de datos que esta conectada. pymysql es lo que permite que sqlalchemy funcione.
