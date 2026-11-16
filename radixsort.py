"""Radix Sort: ordena dígito por dígito, de unidades hacia la izquierda.

Programa con interfaz gráfica: se indica la cantidad de números, se escriben
a mano (o se carga un ejemplo) y se ordenan con Radix Sort. La ventana
sigue abierta hasta que se pulsa «Salir».

Ejecutar con:  python radixsort.py
"""

import random
import re
import time
import tkinter as tk
from tkinter import ttk

# ── Límites de entrada (evitan saturar el programa) ──────────────────────
MAX_CANTIDAD = 1000               # máximo de números por lista
MIN_VALOR = -1_000_000            # valor más pequeño permitido
MAX_VALOR = 1_000_000             # valor más grande permitido
MAX_CARACTERES = 20_000           # texto máximo en el cuadro de números

METODO = "Radix Sort"
DESCRIPCION = "Ordena sin comparar: reparte los números en cubetas por cada dígito."
AYUDA_MANUAL = "Escribe los números separados por espacios, comas o renglones y pulsa «Ordenar»."
AYUDA_EJEMPLO = "Elige un tipo de ejemplo, pulsa «Generar ejemplo» y después «Ordenar»."


# ── Algoritmo ────────────────────────────────────────────────────────────
def _radix_no_negativos(datos):
    """Ordena una lista de enteros >= 0 repartiéndolos en 10 cubetas por dígito."""
    if not datos:
        return datos

    mayor = max(datos)
    exp = 1                               # 1 = unidades, 10 = decenas, ...
    while mayor // exp > 0:
        cubetas = [[] for _ in range(10)]
        for numero in datos:
            cubetas[(numero // exp) % 10].append(numero)
        datos = [numero for cubeta in cubetas for numero in cubeta]
        exp *= 10

    return datos


def radix_sort(numeros):
    """Devuelve una nueva lista ordenada de menor a mayor.

    Solo acepta enteros. Los negativos se ordenan aparte por su valor
    absoluto y luego se invierten, porque Radix trabaja con dígitos.
    """
    negativos = [-n for n in numeros if n < 0]
    no_negativos = [n for n in numeros if n >= 0]

    negativos = [-n for n in reversed(_radix_no_negativos(negativos))]
    return negativos + _radix_no_negativos(no_negativos)


# ── Validación de entradas ───────────────────────────────────────────────
class EntradaInvalida(ValueError):
    """Error de captura con un mensaje listo para mostrar al usuario."""


def convertir_entero(texto):
    """Convierte un texto a entero dentro del rango permitido."""
    recorte = texto if len(texto) <= 15 else texto[:15] + "…"
    if not re.fullmatch(r"[+-]?[0-9]+", texto):
        if re.fullmatch(r"[+-]?([0-9]+[.][0-9]*|[.][0-9]+)", texto):
            raise EntradaInvalida(f"«{recorte}» tiene decimales; solo se aceptan enteros.")
        raise EntradaInvalida(f"«{recorte}» no es un número entero.")
    if len(texto.lstrip("+-")) > 9 or not MIN_VALOR <= int(texto) <= MAX_VALOR:
        raise EntradaInvalida(
            f"«{recorte}» está fuera del rango permitido ({MIN_VALOR:,} a {MAX_VALOR:,})."
        )
    return int(texto)


def leer_cantidad(texto):
    """Valida la cantidad de números (1 a MAX_CANTIDAD)."""
    texto = texto.strip()
    if not texto:
        raise EntradaInvalida("Indica cuántos números vas a ordenar.")
    if not re.fullmatch(r"[0-9]{1,6}", texto) or not 1 <= int(texto) <= MAX_CANTIDAD:
        raise EntradaInvalida(f"La cantidad debe ser un entero entre 1 y {MAX_CANTIDAD:,}.")
    return int(texto)


def separar(texto):
    """Divide el texto en datos separados por espacios, comas o saltos de línea."""
    return re.findall(r"[^\s,;]+", texto)


def leer_numeros(texto, cantidad=None):
    """Convierte el texto en una lista de enteros válidos.

    Si se indica 'cantidad', deben venir exactamente esos números.
    """
    if len(texto) > MAX_CARACTERES:
        raise EntradaInvalida(f"El texto es demasiado largo (máximo {MAX_CARACTERES:,} caracteres).")
    partes = separar(texto)
    if not partes:
        raise EntradaInvalida("Todavía no hay números: escríbelos o carga un ejemplo.")
    if len(partes) > MAX_CANTIDAD:
        raise EntradaInvalida(f"Hay {len(partes):,} números; el máximo es {MAX_CANTIDAD:,}.")
    numeros = []
    for posicion, parte in enumerate(partes, 1):
        try:
            numeros.append(convertir_entero(parte))
        except EntradaInvalida as exc:
            raise EntradaInvalida(f"Dato n.º {posicion}: {exc}") from None
    if cantidad is not None and len(numeros) != cantidad:
        raise EntradaInvalida(
            f"Indicaste {cantidad:,} números, pero hay {len(numeros):,}. "
            "Corrige la cantidad o los números."
        )
    return numeros


# ── Ejemplos listos para cargar ──────────────────────────────────────────
def _casi_ordenados(n):
    datos = sorted(random.randint(0, 10_000) for _ in range(n))
    for _ in range(max(1, n // 20)):          # desordena alrededor del 5 %
        i, j = random.randrange(n), random.randrange(n)
        datos[i], datos[j] = datos[j], datos[i]
    return datos


EJEMPLOS = {
    "Aleatorios": lambda n: [random.randint(MIN_VALOR, MAX_VALOR) for _ in range(n)],
    "Solo positivos pequeños (0 a 99)": lambda n: [random.randint(0, 99) for _ in range(n)],
    "Ya ordenados": lambda n: sorted(random.randint(0, 10_000) for _ in range(n)),
    "En orden inverso": lambda n: sorted((random.randint(0, 10_000) for _ in range(n)), reverse=True),
    "Casi ordenados": _casi_ordenados,
    "Con muchos repetidos": lambda n: [random.randint(1, 5) for _ in range(n)],
    "Todos iguales": lambda n: [7] * n,
}


# ── Interfaz gráfica ─────────────────────────────────────────────────────
VERDE, VERDE_OSCURO, FONDO, TINTA, GRIS, ROJO = "#1F5C4D", "#174539", "#F6F4EF", "#2B2B2B", "#6B6B6B", "#B3261E"


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Ordenamiento con {METODO}")
        escala = self.winfo_fpixels("1i") / 96      # se adapta al zoom de la pantalla
        ancho = min(int(840 * escala), self.winfo_screenwidth() - 80)
        alto = min(int(760 * escala), self.winfo_screenheight() - 120)
        self.geometry(f"{ancho}x{alto}")
        self.minsize(min(ancho, int(700 * escala)), min(alto, int(600 * escala)))
        self.configure(bg=FONDO)
        self.resultado = []
        self._estilos()
        self._construir()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Control-Return>", lambda _: self.ordenar())
        self.caja_numeros.focus_set()

    # -- Construcción ------------------------------------------------------
    def _estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(".", background=FONDO, foreground=TINTA, font=("Segoe UI", 10))
        estilo.configure("Seccion.TLabel", font=("Segoe UI", 10, "bold"), foreground=VERDE)
        estilo.configure("Nota.TLabel", foreground=GRIS, font=("Segoe UI", 9))
        estilo.configure("TButton", padding=(14, 7), background="#E7E3DA", bordercolor="#CFC9BC")
        estilo.map("TButton", background=[("active", "#DAD5C9")])
        estilo.configure("Primario.TButton", background=VERDE, foreground="white",
                         bordercolor=VERDE, font=("Segoe UI", 10, "bold"))
        estilo.map("Primario.TButton", background=[("active", VERDE_OSCURO)])
        estilo.configure("TCombobox", padding=5)
        estilo.configure("TRadiobutton", background=FONDO, focuscolor=FONDO)
        estilo.map("TRadiobutton", background=[("active", FONDO)], indicatorcolor=[("selected", VERDE)])
        estilo.configure("TSpinbox", padding=5)

    def _caja_texto(self, padre, alto):
        """Cuadro de texto con barra de desplazamiento."""
        marco = tk.Frame(padre, bg="#CFC9BC", bd=0)
        caja = tk.Text(marco, height=alto, wrap="word", font=("Consolas", 11), bd=0,
                       padx=10, pady=8, fg=TINTA, bg="white", insertbackground=VERDE,
                       selectbackground=VERDE, selectforeground="white", undo=True)
        barra = ttk.Scrollbar(marco, command=caja.yview)
        caja.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y", padx=(0, 1), pady=1)
        caja.pack(side="left", fill="both", expand=True, padx=(1, 0), pady=1)
        return marco, caja

    def _construir(self):
        cabecera = tk.Frame(self, bg=VERDE)
        cabecera.pack(fill="x")
        tk.Label(cabecera, text=METODO, bg=VERDE, fg="white",
                 font=("Georgia", 24)).pack(anchor="w", padx=24, pady=(16, 0))
        tk.Label(cabecera, text=DESCRIPCION, bg=VERDE, fg="#CFE3DC",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(2, 16))

        cuerpo = ttk.Frame(self, padding=(24, 16, 24, 18))
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.rowconfigure(3, weight=1)
        cuerpo.rowconfigure(7, weight=1)

        # 1) Cantidad y ejemplos
        fila = ttk.Frame(cuerpo)
        fila.grid(row=0, column=0, sticky="ew")
        ttk.Label(fila, text="1. Cantidad de números", style="Seccion.TLabel").pack(side="left")
        self.cantidad = tk.StringVar(value="10")
        ttk.Spinbox(fila, from_=1, to=MAX_CANTIDAD, width=7, textvariable=self.cantidad,
                    font=("Consolas", 11)).pack(side="left", padx=(12, 8))
        ttk.Label(fila, text=f"de 1 a {MAX_CANTIDAD:,}", style="Nota.TLabel").pack(side="left")

        fila = ttk.Frame(cuerpo)
        fila.grid(row=1, column=0, sticky="ew", pady=(14, 8))
        ttk.Label(fila, text="2. Números", style="Seccion.TLabel").pack(side="left")
        self.modo = tk.StringVar(value="manual")
        ttk.Radiobutton(fila, text="Introducirlos manualmente", value="manual", variable=self.modo,
                        command=self._cambiar_modo).pack(side="left", padx=(16, 12))
        ttk.Radiobutton(fila, text="Cargar un ejemplo", value="ejemplo", variable=self.modo,
                        command=self._cambiar_modo).pack(side="left")

        fila = ttk.Frame(cuerpo)
        fila.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.ejemplo = tk.StringVar(value=next(iter(EJEMPLOS)))
        self.lista_ejemplos = ttk.Combobox(fila, textvariable=self.ejemplo, values=list(EJEMPLOS),
                                           state="disabled", width=30)
        self.lista_ejemplos.pack(side="left", padx=(0, 8))
        self.lista_ejemplos.bind("<<ComboboxSelected>>", lambda _: self.generar_ejemplo())
        self.boton_ejemplo = ttk.Button(fila, text="Generar ejemplo", command=self.generar_ejemplo,
                                        state="disabled")
        self.boton_ejemplo.pack(side="left")
        self.contador = ttk.Label(fila, text="", style="Nota.TLabel")
        self.contador.pack(side="right")
        ttk.Label(fila, text=f"enteros de {MIN_VALOR:,} a {MAX_VALOR:,}",
                  style="Nota.TLabel").pack(side="right", padx=12)

        marco, self.caja_numeros = self._caja_texto(cuerpo, 7)
        marco.grid(row=3, column=0, sticky="nsew")
        self.caja_numeros.bind("<KeyRelease>", lambda _: self._actualizar_contador())
        self.caja_numeros.bind("<<Paste>>", self._al_pegar)

        # Botones
        fila = ttk.Frame(cuerpo)
        fila.grid(row=4, column=0, sticky="ew", pady=14)
        ttk.Button(fila, text="Ordenar", style="Primario.TButton", command=self.ordenar).pack(side="left")
        ttk.Button(fila, text="Limpiar", command=self.limpiar).pack(side="left", padx=8)
        ttk.Button(fila, text="Copiar resultado", command=self.copiar_resultado).pack(side="left")
        ttk.Button(fila, text="Salir", command=self.destroy).pack(side="right")

        # Mensajes y resultado
        self.estado = tk.Label(cuerpo, text=AYUDA_MANUAL,
                               bg=FONDO, fg=GRIS, font=("Segoe UI", 10), anchor="w", justify="left",
                               wraplength=700)
        self.estado.grid(row=5, column=0, sticky="ew")
        cuerpo.bind("<Configure>", lambda e: self.estado.configure(wraplength=max(200, e.width - 60)))
        ttk.Label(cuerpo, text="Resultado", style="Seccion.TLabel").grid(row=6, column=0, sticky="w", pady=(12, 6))
        marco, self.caja_resultado = self._caja_texto(cuerpo, 7)
        marco.grid(row=7, column=0, sticky="nsew")
        self.caja_resultado.configure(state="disabled", bg="#FBFAF7")
        self._actualizar_contador()

    # -- Utilidades --------------------------------------------------------
    def _mensaje(self, texto, tipo="info"):
        color = {"info": GRIS, "ok": VERDE, "error": ROJO}[tipo]
        simbolo = {"info": "", "ok": "✔ ", "error": "✖ "}[tipo]
        self.estado.configure(text=simbolo + texto, fg=color)

    def _poner_numeros(self, numeros):
        """Reemplaza el contenido del cuadro (aunque esté bloqueado en modo ejemplo)."""
        self.caja_numeros.configure(state="normal")
        self.caja_numeros.delete("1.0", "end")
        self.caja_numeros.insert("1.0", ", ".join(map(str, numeros)))
        self._bloquear_cuadro_si_es_ejemplo()
        self._actualizar_contador()

    def _bloquear_cuadro_si_es_ejemplo(self):
        ejemplo = self.modo.get() == "ejemplo"
        self.caja_numeros.configure(state="disabled" if ejemplo else "normal",
                                    bg="#FBFAF7" if ejemplo else "white")

    def _cambiar_modo(self):
        """Alterna entre escribir los números a mano y cargar un ejemplo."""
        ejemplo = self.modo.get() == "ejemplo"
        self.lista_ejemplos.configure(state="readonly" if ejemplo else "disabled")
        self.boton_ejemplo.configure(state="normal" if ejemplo else "disabled")
        self._bloquear_cuadro_si_es_ejemplo()
        self._poner_resultado([])
        if ejemplo:
            self.generar_ejemplo()
        else:                                 # los números quedan para poder editarlos
            self._mensaje(AYUDA_MANUAL)
            self.caja_numeros.focus_set()

    def _poner_resultado(self, numeros):
        self.resultado = numeros
        self.caja_resultado.configure(state="normal")
        self.caja_resultado.delete("1.0", "end")
        self.caja_resultado.insert("1.0", ", ".join(map(str, numeros)))
        self.caja_resultado.configure(state="disabled")

    def _actualizar_contador(self):
        escritos = len(separar(self.caja_numeros.get("1.0", "end")))
        self.contador.configure(text=f"{escritos:,} escritos")

    def _al_pegar(self, _evento):
        """Rechaza pegar textos enormes antes de que lleguen al cuadro."""
        try:
            pegado = self.clipboard_get()
        except tk.TclError:
            return "break"                    # el portapapeles no tiene texto
        if len(pegado) + len(self.caja_numeros.get("1.0", "end")) > MAX_CARACTERES:
            self._mensaje(f"Lo que intentas pegar es demasiado largo (máximo {MAX_CARACTERES:,} caracteres).", "error")
            return "break"
        self.after_idle(self._actualizar_contador)
        return None

    # -- Acciones ----------------------------------------------------------
    def generar_ejemplo(self):
        try:
            cantidad = leer_cantidad(self.cantidad.get())
        except EntradaInvalida as exc:
            self._mensaje(str(exc), "error")
            return
        self._poner_numeros(EJEMPLOS[self.ejemplo.get()](cantidad))
        self._poner_resultado([])
        self._mensaje(f"Ejemplo «{self.ejemplo.get()}» con {cantidad:,} números cargado. Pulsa «Ordenar».")

    def ordenar(self):
        try:
            cantidad = leer_cantidad(self.cantidad.get())
            numeros = leer_numeros(self.caja_numeros.get("1.0", "end"), cantidad)
        except EntradaInvalida as exc:
            self._poner_resultado([])
            self._mensaje(str(exc), "error")
            return
        inicio = time.perf_counter()
        ordenados = radix_sort(numeros)
        milisegundos = (time.perf_counter() - inicio) * 1000
        self._poner_resultado(ordenados)
        self._mensaje(
            f"{cantidad:,} números ordenados con {METODO} en {milisegundos:.3f} ms.   "
            f"Menor: {ordenados[0]:,}   Mayor: {ordenados[-1]:,}", "ok")

    def limpiar(self):
        self._poner_numeros([])
        self._poner_resultado([])
        self._mensaje(AYUDA_EJEMPLO if self.modo.get() == "ejemplo" else AYUDA_MANUAL)
        self.caja_numeros.focus_set()

    def copiar_resultado(self):
        if not self.resultado:
            self._mensaje("Todavía no hay un resultado para copiar.", "error")
            return
        self.clipboard_clear()
        self.clipboard_append(", ".join(map(str, self.resultado)))
        self._mensaje("Resultado copiado al portapapeles.", "ok")


def main():
    try:                                      # texto nítido en pantallas de alta resolución
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    Aplicacion().mainloop()


if __name__ == "__main__":
    main()
