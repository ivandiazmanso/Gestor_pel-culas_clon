# app.py
# Archivo principal de la aplicación web Watchlist (Películas por Ver).

import os
from flask import Flask, render_template, request, session, redirect, url_for
from pelicula import Pelicula

# Inicializamos la aplicación Flask
app = Flask(__name__)

# Clave secreta obligatoria para cifrar las cookies de 'session'
app.secret_key = os.urandom(24)

# FUNCIONES AUXILIARES PARA GESTIONAR LA SESIÓN

def obtener_peliculas():
    """
    Lee la lista de diccionarios guardada en session['peliculas']
    y la convierte de nuevo en una lista de objetos Pelicula.
    """
    lista_objetos = []
    # Si todavía no existe la clave en sesión, devuelve una lista vacía
    datos_sesion = session.get("peliculas", [])

    for item in datos_sesion:
        try:
            # Reconstruimos cada objeto usando el método de la clase Pelicula
            pelicula = Pelicula.desde_diccionario(item)
            lista_objetos.append(pelicula)
        except (KeyError, ValueError, TypeError):
            # Si algún dato estuviera corrupto, lo ignoramos para que no rompa la app
            continue

    return lista_objetos


def guardar_peliculas(lista_objetos):
    """
    Convierte una lista de objetos Pelicula en una lista de diccionarios
    y la guarda en session['peliculas'].
    """
    lista_diccionarios = []
    for pelicula in lista_objetos:
        lista_diccionarios.append(pelicula.a_diccionario())

    session["peliculas"] = lista_diccionarios
    # Indicamos a Flask que la sesión ha cambiado para asegurar que se guarde
    session.modified = True

def generar_nuevo_id(lista_objetos):
    """
    Genera un ID numérico único buscando el ID más alto actual y sumando 1.
    """
    if not lista_objetos:
        return 1
    id_maximo = 0
    for p in lista_objetos:
        if p.id > id_maximo:
            id_maximo = p.id
    return id_maximo + 1


# RUTAS DE LA APLICACIÓN (CRUD)

@app.route("/", methods=["GET"])
def inicio():
    """
    OPERACIÓN READ (Leer/Consultar):
    Muestra la página principal con el formulario y la lista de películas.
    Permite filtrar por 'todas', 'pendiente' o 'vista'.
    """
    peliculas = obtener_peliculas()

    # Leemos el filtro opcional de la URL (ej: /?filtro=pendiente)
    filtro = request.args.get("filtro", "todas")
    if filtro not in ("todas", "pendiente", "vista"):
        filtro = "todas"

    # Filtramos la lista según lo que haya elegido el usuario
    peliculas_filtradas = []
    for p in peliculas:
        if filtro == "todas" or p.estado == filtro:
            peliculas_filtradas.append(p)

    # Calculamos contadores para mostrar un resumen en pantalla
    total = len(peliculas)
    pendientes = 0
    vistas = 0
    for p in peliculas:
        if p.estado == "pendiente":
            pendientes += 1
        else:
            vistas += 1

    # Recuperamos y borramos los mensajes temporales de error o éxito (si los hay)
    error = session.pop("error", None)
    mensaje = session.pop("mensaje", None)

    return render_template(
        "index.html",
        peliculas=peliculas_filtradas,
        filtro_actual=filtro,
        total=total,
        pendientes=pendientes,
        vistas=vistas,
        error=error,
        mensaje=mensaje
    )

@app.route("/agregar", methods=["POST"])
def agregar_pelicula():
    """
    OPERACIÓN CREATE (Crear/Añadir):
    Recibe los datos del formulario por POST, los valida y guarda la nueva película.
    """
    try:
        # Obtenemos los datos del formulario HTML (request.form)
        titulo = request.form.get("titulo", "").strip()
        director = request.form.get("director", "").strip()
        genero = request.form.get("genero", "").strip()

        # Validación en el servidor: comprobamos que no falte ningún campo
        if not titulo or not director or not genero:
            session["error"] = "Todos los campos (título, director y género) son obligatorios."
            return redirect(url_for("inicio"))

        # Cargamos las películas actuales y generamos un nuevo ID
        peliculas = obtener_peliculas()
        nuevo_id = generar_nuevo_id(peliculas)

        # Creamos el objeto Pelicula (aquí también actúan los setters de validación)
        nueva_pelicula = Pelicula(nuevo_id, titulo, director, genero)

        # Añadimos el objeto a la lista y guardamos en sesión
        peliculas.append(nueva_pelicula)
        guardar_peliculas(peliculas)

        session["mensaje"] = f"Película '{nueva_pelicula.titulo}' añadida a tu Watchlist."

    except ValueError as e:
        # Capturamos errores de validación lanzados por los setters de la clase
        session["error"] = str(e)
    except Exception:
        # Captura general para evitar que la aplicación se caiga inesperadamente
        session["error"] = "Ocurrió un error inesperado al intentar añadir la película."

    return redirect(url_for("inicio"))


@app.route("/cambiar_estado/<int:id_pelicula>", methods=["POST"])
def cambiar_estado(id_pelicula):
    """
    OPERACIÓN UPDATE (Actualizar):
    Alterna el estado de una película entre 'pendiente' y 'vista' usando su setter.
    """
    try:
        peliculas = obtener_peliculas()
        encontrada = False

        for p in peliculas:
            if p.id == id_pelicula:
                # Cambiamos el estado usando el getter y setter de la clase Pelicula
                if p.estado == "pendiente":
                    p.estado = "vista"
                    session["mensaje"] = f"Has marcado '{p.titulo}' como vista."
                else:
                    p.estado = "pendiente"
                    session["mensaje"] = f"Has vuelto a marcar '{p.titulo}' como pendiente."
                encontrada = True
                break

        if encontrada:
            guardar_peliculas(peliculas)
        else:
            session["error"] = "No se encontró la película que intentabas actualizar."

    except ValueError as e:
        session["error"] = str(e)
    except Exception:
        session["error"] = "No se pudo actualizar el estado de la película."

    return redirect(url_for("inicio"))


@app.route("/eliminar/<int:id_pelicula>", methods=["POST"])
def eliminar_pelicula(id_pelicula):
    """
    OPERACIÓN DELETE (Eliminar):
    Elimina de la sesión la película cuyo ID coincida con el recibido.
    """
    try:
        peliculas = obtener_peliculas()
        nueva_lista = []
        titulo_borrado = None

        # Construimos una nueva lista excluyendo la película a borrar
        for p in peliculas:
            if p.id == id_pelicula:
                titulo_borrado = p.titulo
            else:
                nueva_lista.append(p)

        if titulo_borrado is not None:
            guardar_peliculas(nueva_lista)
            session["mensaje"] = f"Película '{titulo_borrado}' eliminada correctamente."
        else:
            session["error"] = "No se encontró la película que intentabas eliminar."

    except Exception:
        session["error"] = "Ocurrió un error al intentar eliminar la película."

    return redirect(url_for("inicio"))


# Punto de entrada para ejecutar el servidor en modo desarrollo
if __name__ == "__main__":
    app.run(debug=True)