import sqlite3
from sqlite3 import Error
import csv

conn = sqlite3.connect('taller_mecanico.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clave TEXT UNIQUE,
        nombre TEXT NOT NULL,
        rfc TEXT NOT NULL,
        correo TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS servicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clave TEXT UNIQUE,
        nombre TEXT NOT NULL,
        costo REAL NOT NULL CHECK (costo > 0.00)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT UNIQUE,
        fecha DATE DEFAULT (datetime('now', 'localtime')),
        cliente_id INTEGER,
        monto REAL NOT NULL,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalle_notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nota_id INTEGER,
        servicio_id INTEGER,
        FOREIGN KEY(nota_id) REFERENCES notas(id),
        FOREIGN KEY(servicio_id) REFERENCES servicios(id)
    )
''')
conn.commit()
conn.close()

def registrar_nota():
    cliente_clave = input("Ingrese la clave del cliente: ")

    cursor.execute("SELECT * FROM clientes WHERE clave=?", (cliente_clave,))
    cliente = cursor.fetchone()

    if cliente is None:
        print("Cliente no encontrado. Por favor, registre al cliente primero.")
        return

    cursor.execute("SELECT * FROM servicios")
    servicios = cursor.fetchall()

    if not servicios:
        print("No hay servicios disponibles. Por favor, registre servicios primero.")
        return

    print("Servicios disponibles:")
    for servicio in servicios:
        print(f"{servicio[1]}. {servicio[2]} - ${servicio[3]}")

    servicios_seleccionados = input("Ingrese las claves de los servicios separadas por comas: ")
    servicios_ids = [int(id) for id in servicios_seleccionados.split(',')]

    monto_total = sum(servicios[servicio_id - 1][3] for servicio_id in servicios_ids)

    cursor.execute("SELECT COUNT(*) FROM notas")
    num_notas = cursor.fetchone()[0] + 1
    folio = num_notas

    cursor.execute("INSERT INTO notas (folio, cliente_id, monto) VALUES (?, ?, ?)",
                   (folio, cliente[0], monto_total))

    nota_id = cursor.lastrowid

    for servicio_id in servicios_ids:
        cursor.execute("INSERT INTO detalle_notas (nota_id, servicio_id) VALUES (?, ?)",
                       (nota_id, servicio_id))

    print(f"Nota registrada con éxito. Folio: {folio}")

def cancelar_nota():
    folio_nota = input("Ingrese el folio de la nota a cancelar: ")
    cursor.execute("SELECT * FROM notas WHERE folio=? AND NOT EXISTS (SELECT 1 FROM notas_canceladas WHERE notas.id = notas_canceladas.nota_id)",
                   (folio_nota,))
    nota = cursor.fetchone()
    if nota is None:
        print("Nota no encontrada o ya está cancelada.")
        return
    print(f"Detalles de la nota {folio_nota}:")
    cursor.execute("SELECT servicios.nombre, servicios.costo FROM servicios "
                   "INNER JOIN detalle_notas ON servicios.id = detalle_notas.servicio_id "
                   "WHERE detalle_notas.nota_id=?", (nota[0],))
    servicios = cursor.fetchall()
    #confirmacion
    for servicio in servicios:
        print(f"Servicio: {servicio[0]}, Costo: ${servicio[1]}")
    confirmacion = input("¿Está seguro de que desea cancelar esta nota? (Sí/No): ")
    if confirmacion.lower() == "sí" or confirmacion.lower() == "si":
        cursor.execute("INSERT INTO notas_canceladas (nota_id) VALUES (?)", (nota[0],))
        print(f"Nota {folio_nota} cancelada correctamente.")
    else:
        print("Cancelación de nota cancelada.")
def recuperar_nota():
    #notas canceladas
    cursor.execute("SELECT notas.folio FROM notas "
                   "INNER JOIN notas_canceladas ON notas.id = notas_canceladas.nota_id")
    notas_canceladas = cursor.fetchall()
    if not notas_canceladas:
        print("No hay notas canceladas.")
        return
    print("Notas canceladas:")
    for nota in notas_canceladas:
        print(f"- {nota[0]}")
    #folio para recuperar
    folio_nota = input("Ingrese el folio de la nota a recuperar (o 'x' para cancelar): ")
    if folio_nota.lower() == "x":
        print("Operación de recuperación cancelada.")
        return
    #checar si esta cancelada
    cursor.execute("SELECT notas.id FROM notas "
                   "INNER JOIN notas_canceladas ON notas.id = notas_canceladas.nota_id "
                   "WHERE notas.folio=?", (folio_nota,))
    nota_id = cursor.fetchone()

    if nota_id is None:
        print("Nota no encontrada en la lista de notas canceladas.")
        return
    # mostrar nota cancelada
    cursor.execute("SELECT servicios.nombre, servicios.costo FROM servicios "
                   "INNER JOIN detalle_notas ON servicios.id = detalle_notas.servicio_id "
                   "WHERE detalle_notas.nota_id=?", (nota_id[0],))
    servicios = cursor.fetchall()

    for servicio in servicios:
        print(f"Servicio: {servicio[0]}, Costo: ${servicio[1]}")

    confirmacion = input("¿Está seguro de que desea recuperar esta nota? (Sí/No): ")
    if confirmacion.lower() == "sí" or confirmacion.lower() == "si":
        cursor.execute("DELETE FROM notas_canceladas WHERE nota_id=?", (nota_id[0],))
        print(f"Nota {folio_nota} recuperada correctamente.")
    else:
        print("Recuperación de nota cancelada.")

def consultar_notas_por_periodo():
    # Solicitar fechas inicio y fin
    fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD): ")
    fecha_fin = input("Ingrese la fecha de fin (YYYY-MM-DD, o presione Enter para usar la fecha actual): ")
    if not fecha_fin:
        fecha_fin = "date('now')"
    try:
        #notas en el período 
        cursor.execute("SELECT notas.folio, notas.fecha, clientes.nombre, notas.monto FROM notas "
                       "INNER JOIN clientes ON notas.cliente_id = clientes.id "
                       "WHERE notas.fecha BETWEEN ? AND ?",
                       (fecha_inicio, fecha_fin))
        notas = cursor.fetchall()
        if not notas:
            print("No hay notas emitidas para el período especificado.")
            return

        # promedio de las notas
        total_monto = sum(nota[3] for nota in notas)
        monto_promedio = total_monto / len(notas)

        #imprimir reporte y promedio
        print("=== Reporte de Notas ===")
        for nota in notas:
            print(f"Folio: {nota[0]}, Fecha: {nota[1]}, Cliente: {nota[2]}, Monto: ${nota[3]}")
        print(f"Monto Promedio: ${monto_promedio:.2f}")
    except Exception:
        print(f"Error al consultar notas por período:")

def agregar_cliente():
    # Solicitar detalles del cliente
    nombre = input("Ingrese el nombre completo del cliente: ")
    rfc = input("Ingrese el RFC del cliente: ")
    correo = input("Ingrese el correo electrónico del cliente: ")
    try:
        # clave cliente
        cursor.execute("SELECT COUNT(*) FROM clientes")
        num_clientes = cursor.fetchone()[0] + 1
        clave_cliente = num_clientes
        # Insertar el cliente 
        cursor.execute("INSERT INTO clientes (clave, nombre, rfc, correo) VALUES (?, ?, ?, ?)",
                       (clave_cliente, nombre, rfc, correo))
        print(f"Cliente registrado correctamente. Clave del cliente: {clave_cliente}")
    except Exception:
        print(f"Error al agregar el cliente: ")
def menu_consultas_clientes():
    while True:
        print("=== Menú de Consultas y Reportes de Clientes ===")
        print("1. Listado de clientes ordenado por clave")
        print("2. Listado de clientes ordenado por nombre")
        print("3. Volver al menú anterior")
        opcion_clientes = input("Seleccione una opción: ")

        if opcion_clientes == "1":
            listar_clientes_por_clave()
        elif opcion_clientes == "2":
            listar_clientes_por_nombre()
        elif opcion_clientes == "3":
            print("Volviendo al menú anterior...")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida para Clientes.")
def listar_clientes_por_clave():
    try:
        #clientes clave
        cursor.execute("SELECT clave, nombre, rfc, correo FROM clientes ORDER BY clave")
        clientes = cursor.fetchall()

        if clientes:
            print("=== Listado de Clientes Ordenado por Clave ===")
            print("Clave\tNombre\tRFC\tCorreo")
            for cliente in clientes:
                print(f"{cliente[0]}\t{cliente[1]}\t{cliente[2]}\t{cliente[3]}")
        else:
            print("No hay clientes registrados.")

    except Exception:
        print(f"Error al listar los clientes:")

def listar_clientes_por_nombre():
    try:
        #clientes por nombre
        cursor.execute("SELECT clave, nombre, rfc, correo FROM clientes ORDER BY nombre")
        clientes = cursor.fetchall()

        if clientes:
            print("=== Listado de Clientes Ordenado por Nombre ===")
            print("Clave\tNombre\tRFC\tCorreo")
            for cliente in clientes:
                print(f"{cliente[0]}\t{cliente[1]}\t{cliente[2]}\t{cliente[3]}")
        else:
            print("No hay clientes registrados.")

    except Exception:
        print(f"Error al listar los clientes:")

def menu_clientes():
    while True:
        print("=== Menú Clientes ===")
        print("1. Agregar un cliente")
        print("2. Consultas  y reportes")
        print("3. Volver al menú anterior")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            agregar_cliente()
        elif opcion == "2":
            menu_consultas_clientes()
        elif opcion == "3":
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

def agregar_servicio():
    # detalles del servicio
    nombre_servicio = input("Ingrese el nombre del servicio: ")
    costo_servicio = float(input("Ingrese el costo del servicio (mayor a 0.00): "))

    # verificar costo
    while costo_servicio <= 0:
        print("El costo del servicio debe ser mayor a 0.00.")
        costo_servicio = float(input("Ingrese el costo del servicio (mayor a 0.00): "))
    try:
        #clave del servicio
        cursor.execute("SELECT COUNT(*) FROM servicios")
        num_servicios = cursor.fetchone()[0] + 1
        clave_servicio = f"{num_servicios}"
        # Insertar el servicio 
        cursor.execute("INSERT INTO servicios (clave, nombre, costo) VALUES (?, ?, ?)",
                       (clave_servicio, nombre_servicio, costo_servicio))
        print(f"Servicio registrado correctamente. Clave del servicio: {clave_servicio}")
    except Exception:
        print(f"Error al agregar el servicio:")

def buscar_servicio_por_clave():
    # pedir clave
    clave_servicio = input("Ingrese la clave del servicio: ")
    try:
        # buscar servicio por clave
        cursor.execute("SELECT nombre, costo FROM servicios WHERE clave = ?", (clave_servicio,))
        servicio = cursor.fetchone()
        if servicio:
            print(f"Nombre del servicio: {servicio[0]}")
            print(f"Costo del servicio: ${servicio[1]:.2f}")
        else:
            print("No se encontró ningún servicio con esa clave.")
    except Exception:
        print(f"Error al buscar el servicio:")

def buscar_servicio_por_nombre():
    # pedir nombre del servicio
    nombre_servicio = input("Ingrese el nombre del servicio: ")
    try:
        # Consultar servicio por nombre (ignorar diferencias entre mayúsculas y minúsculas)
        cursor.execute("SELECT clave, nombre, costo FROM servicios WHERE LOWER(nombre) = LOWER(?)", (nombre_servicio,))
        servicio = cursor.fetchone()

        if servicio:
            print(f"Clave del servicio: {servicio[0]}")
            print(f"Nombre del servicio: {servicio[1]}")
            print(f"Costo del servicio: ${servicio[2]:.2f}")
        else:
            print("No se encontró ningún servicio con ese nombre.")
    except Exception:
        print(f"Error al buscar el servicio:")
def listar_servicios_por_clave():
    try:
        # Buscar servicios ordenados por clave
        cursor.execute("SELECT clave, nombre, costo FROM servicios ORDER BY clave")
        servicios = cursor.fetchall()
        if servicios:
            print("=== Listado de Servicios Ordenado por Clave ===")
            print("Clave\tNombre\tCosto")
            for servicio in servicios:
                print(f"{servicio[0]}\t{servicio[1]}\t${servicio[2]:.2f}")
        else:
            print("No hay servicios registrados.")

    except Exception as e:
        print(f"Error al listar los servicios:")

def listar_servicios_por_nombre():
    try:
        # Consultar servicios ordenados por nombre
        cursor.execute("SELECT clave, nombre, costo FROM servicios ORDER BY nombre")
        servicios = cursor.fetchall()
        if servicios:
            print("=== Listado de Servicios Ordenado por Nombre ===")
            print("Clave\tNombre\tCosto")
            for servicio in servicios:
                print(f"{servicio[0]}\t{servicio[1]}\t${servicio[2]:.2f}")
        else:
            print("No hay servicios registrados.")
    except Exception:
        print(f"Error al listar los servicios:")

# Menú de servicios
def menu_servicios():
    while True:
        print("=== Menú Servicios ===")
        print("1. Agregar un servicio")
        print("2. Búsqueda por clave de servicio")
        print("3. Búsqueda por nombre de servicio")
        print("4. Listado de servicios ordenado por clave")
        print("5. Listado de servicios ordenado por nombre")
        print("6. Volver al menú anterior")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            agregar_servicio()
        elif opcion == "2":
            buscar_servicio_por_clave()
        elif opcion == "3":
            buscar_servicio_por_nombre()
        elif opcion == "4":
          listar_servicios_por_clave()
        elif opcion == "5":
            listar_servicios_por_nombre()
        elif opcion == "6":
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")
#MENU PRINCIPAL
def mostrar_menu():
    print("=== Menú ===")
    print("1. Notas")
    print("2. Clientes")
    print("3. Servicios")
    print("4. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        if opcion=="1":
          while True:
            print("=== Menú ===")
            print("1. Registrar una nota")
            print("2. Cancelar una nota")
            print("3. Recuperar una nota cancelada")
            print("4. Consultas y reportes de notas")
            print("5. Volver al menú principal")
            opcion = input("Seleccione una opción: ")
            if opcion == "1":
              registrar_nota()
            elif opcion == "2":
              cancelar_nota()
            elif opcion == "3":
              recuperar_nota()
            elif opcion == "4":
              consultar_notas_por_periodo()
            elif opcion == "5":
                print("Volviendo al menú principal...")
                break
            else:
                print("Opción no válida. Por favor, seleccione una opción válida.")
            #cerrar conexion
            conn.commit()
            conn.close()
        elif opcion == "2":
              menu_clientes()
              if opcion == "1":
                agregar_cliente()
              elif opcion == "2":
                menu_consultas_clientes()
              elif opcion == "3":
                    print("Volviendo al menú principal...")
                    break
              else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
        elif opcion == "3":
             menu_servicios()
        elif opcion == "4":
              print("¡Hasta luego!")
              break
        else:
              print("Opción no válida. Por favor, seleccione una opción válida.")

if __name__ == "__main__":
    main()