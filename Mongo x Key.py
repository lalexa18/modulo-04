import redis
import json
from flask import Flask

# Configuración inicial de Flask y conexión a KeyDB
app = Flask(__name__)

# Conexión a KeyDB (se puede ajustar el puerto si no es el 6379 por defecto)
keydb = redis.Redis(host='localhost', port=6379, db=0)

# Función para generar un nuevo ID de libro
def generar_id():
    return keydb.incr('libro_id')  # Incrementar el ID de libro cada vez que se agrega uno nuevo

# Agregar nuevo libro
def agregar_libro():
    id_libro = generar_id()  # Genera un nuevo ID para el libro
    titulo = input("Título del libro: ")
    autor = input("Autor del libro: ")
    anio = int(input("Año de publicación: "))

    # Crear un diccionario con los datos del libro
    nuevo_libro = {
        'titulo': titulo,
        'autor': autor,
        'anio': anio
    }

    # Almacenar el libro en KeyDB como un hash
    keydb.hset(f'libro:{id_libro}', mapping=nuevo_libro)
    print(f"Libro '{titulo}' agregado exitosamente con ID {id_libro}.")

# Actualizar libro existente
def actualizar_libro():
    id_libro = input("ID del libro a actualizar: ")

    if keydb.exists(f'libro:{id_libro}'):
        nuevo_titulo = input("Nuevo título del libro: ") or keydb.hget(f'libro:{id_libro}', 'titulo').decode('utf-8')
        nuevo_autor = input("Nuevo autor del libro: ") or keydb.hget(f'libro:{id_libro}', 'autor').decode('utf-8')
        nuevo_anio = input("Nuevo año de publicación: ") or keydb.hget(f'libro:{id_libro}', 'anio').decode('utf-8')

        # Actualizar el hash del libro
        keydb.hset(f'libro:{id_libro}', mapping={
            'titulo': nuevo_titulo,
            'autor': nuevo_autor,
            'anio': nuevo_anio
        })
        print(f"Libro ID '{id_libro}' actualizado exitosamente.")
    else:
        print(f"Libro ID '{id_libro}' no encontrado.")

# Eliminar libro existente
def eliminar_libro():
    id_libro = input("ID del libro a eliminar: ")

    if keydb.exists(f'libro:{id_libro}'):
        keydb.delete(f'libro:{id_libro}')
        print(f"Libro ID '{id_libro}' eliminado exitosamente.")
    else:
        print(f"Libro ID '{id_libro}' no encontrado.")

# Ver listado de libros
def ver_libros():
    keys = keydb.keys('libro:*')

    if keys:
        print("Listado de libros:")
        for key in keys:
            libro = keydb.hgetall(key)
            libro_decoded = {k.decode('utf-8'): v.decode('utf-8') for k, v in libro.items()}
            print(f"ID: {key.decode('utf-8').split(':')[1]}, Título: {libro_decoded['titulo']}, Autor: {libro_decoded['autor']}, Año: {libro_decoded['anio']}")
    else:
        print("No hay libros en la biblioteca.")

# Buscar libro por título
def buscar_libro():
    titulo = input("Título del libro a buscar: ").lower()
    keys = keydb.keys('libro:*')

    libros_encontrados = []
    for key in keys:
        libro = keydb.hgetall(key)
        titulo_libro = libro.get(b'titulo', b'').decode('utf-8').lower()
        if titulo in titulo_libro:
            libros_encontrados.append((key, libro))

    if libros_encontrados:
        print("Libros encontrados:")
        for key, libro in libros_encontrados:
            libro_decoded = {k.decode('utf-8'): v.decode('utf-8') for k, v in libro.items()}
            print(f"ID: {key.decode('utf-8').split(':')[1]}, Autor: {libro_decoded['autor']}, Año: {libro_decoded['anio']}")
    else:
        print("No se encontraron libros con ese título.")

# Función principal del menú
def menu():
    while True:
        print("\n--- Biblioteca de Libros (KeyDB) ---")
        print("1. Agregar nuevo libro")
        print("2. Actualizar libro existente")
        print("3. Eliminar libro existente")
        print("4. Ver listado de libros")
        print("5. Buscar libro por título")
        print("6. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            agregar_libro()
        elif opcion == '2':
            actualizar_libro()
        elif opcion == '3':
            eliminar_libro()
        elif opcion == '4':
            ver_libros()
        elif opcion == '5':
            buscar_libro()
        elif opcion == '6':
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

# Ejecutar el programa
if __name__ == "__main__":
    menu()