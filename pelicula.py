class Pelicula:
    """
        Representa una película dentro de la Watchlist.
        Usa atributos privados y propiedades
        para validar los datos antes de guardarlos.
    """

    # Estados permitidos para cualquier película
    ESTADOS_VALIDOS = ("pendiente", "vista")

    def __init__(self, id_pelicula, titulo, director, genero, estado="pendiente"):
        """
            Constructor de la clase Pelicula.
            Asigna los valores para asegurar la validación.
         """
        self.__id = id_pelicula
        self.titulo = titulo
        self.director = director
        self.genero = genero
        self.estado = estado

    # Getter de ID (solo lectura)
    @property
    def id(self):
        return self.__id

    # Getter y Setter de TITULO
    @property
    def titulo(self):
        return self.__titulo

    @titulo.setter
    def titulo(self, valor):
        # Validamos que sea texto y que no esté vacío al quitar espacios
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El título de la película no puede estar vacío.")
        self.__titulo = valor.strip()

    # Getter y Setter de DIRECTOR
    @property
    def director(self):
        return self.__director

    @director.setter
    def director(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre del director no puede estar vacío.")
        self.__director = valor.strip()

    # Getter y Setter de GÉNERO
    @property
    def genero(self):
        return self.__genero

    @genero.setter
    def genero(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El género de la película no puede estar vacío.")
        self.__genero = valor.strip()

    # Getter y Setter de ESTADO
    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, valor):
        # Comprobamos que el estado esté en la tupla de estados válidos
        if not isinstance(valor, str):
            raise ValueError("El estado debe ser una cadena de texto.")
        valor_limpio = valor.strip().lower()
        if valor_limpio not in self.ESTADOS_VALIDOS:
            raise ValueError("El estado solo puede ser 'pendiente' o 'vista'.")
        self.__estado = valor_limpio

    def a_diccionario(self):
        """
            Convierte el objeto Pelicula en un diccionario estándar de Python
            para poder guardarlo en Flask 'session'.
        """
        return {
            "id": self.__id,
            "titulo": self.__titulo,
            "director": self.__director,
            "genero": self.__genero,
            "estado": self.__estado
        }

    @classmethod
    def desde_diccionario(cls, datos):
        """
            Reconstruye un objeto Pelicula a partir de un diccionario
            recuperado de la sesión de Flask.
        """
        return cls(
            id_pelicula=datos["id"],
            titulo=datos["titulo"],
            director=datos["director"],
            genero=datos["genero"],
            estado=datos.get("estado", "pendiente")
        )