import datetime
import csv
import os

archivo_csv = "notas.csv"
notas = {}

def generar_folio():
    return len(notas) + 1

def validar_rfc(rfc):
    if len(rfc) != 13:
        print("Error: El RFC debe tener exactamente 13 caracteres.")
        return False
    return True

def guardar_datos_csv():
    with open(archivo_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Folio", "Fecha", "Cliente", "RFC", "Email", "Detalle", "Monto Total", "Cancelada"])
        for folio, nota in notas.items():
            detalle = "\n".join([f"{item['servicio']}: ${item['costo']:.2f}" for item in nota['detalle']])
            writer.writerow([folio, nota['fecha'].strftime("%Y-%m-%d"), nota['cliente'], nota['rfc'],
                             nota['email'], detalle, f"${nota['monto_total']:.2f}", nota['cancelada']])
def cargar_datos_csv():
    if os.path.exists(archivo_csv):
        with open(archivo_csv, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                folio = int(row["Folio"])
                fecha = datetime.datetime.strptime(row["Fecha"], "%Y-%m-%d")
                cliente = row["Cliente"]
                rfc = row["RFC"]
                email = row["Email"]
                detalle = []
                for item in row["Detalle"].split("\n"):
                    servicio, costo = item.split(": $")
                    detalle.append({"servicio": servicio, "costo": float(costo)})
                monto_total = float(row["Monto Total"].replace("$", ""))
                cancelada = row["Cancelada"] == "True"
                notas[folio] = {
                    "fecha": fecha,
                    "cliente": cliente,
                    "rfc": rfc,
                    "email": email,
                    "detalle": detalle,
                    "monto_total": monto_total,
                    "cancelada": cancelada
                }
cargar_datos_csv()
# Función para registrar una nueva nota
def registrar_nota():
    try:
        folio = generar_folio()
        fecha = input("Ingrese la fecha de la nota (YYYY-MM-DD): ")
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
        if fecha > datetime.datetime.now():
            print("Error: La fecha no puede ser posterior a la fecha actual.")
            return
        cliente = input("Ingrese el nombre del cliente: ")
        rfc = input("Ingrese el RFC del cliente: ")
        if not validar_rfc(rfc): 
            return
        email = input("Ingrese el correo electrónico del cliente: ")
        detalle = []
        while True:
            servicio = input("Ingrese el nombre del servicio (o escriba 'fin' para terminar): ")
            if servicio.lower() == "fin":
                break
            costo = float(input("Ingrese el costo del servicio: "))
            if costo <= 0:
                print("Error: El costo debe ser mayor que cero.")
                return
            detalle.append({"servicio": servicio, "costo": costo})

        monto_total = sum(item["costo"] for item in detalle)

        # Agregar la nota al diccionario
        notas[folio] = {
            "fecha": fecha,
            "cliente": cliente,
            "rfc": rfc,
            "email": email,
            "detalle": detalle,
            "monto_total": monto_total,
            "cancelada": False 
        }
        guardar_datos_csv()

        print("Nota registrada con éxito. Folio:", folio)
    except Exception :
        print(f"Ocurrió un error inesperado:")
# consultar una nota por folio
def consultar_por_folio():
    try:
        folio = int(input("Ingrese el folio de la nota a consultar: "))
        if folio in notas:
            nota = notas[folio]
            print(f"Folio: {folio}")
            print(f"Fecha: {nota['fecha'].strftime('%Y-%m-%d')}")
            print(f"Cliente: {nota['cliente']}")
            print(f"RFC: {nota['rfc']}")
            print(f"Correo electrónico: {nota['email']}")
            print("Detalle:")
            for servicio in nota['detalle']:
                print(f"  - {servicio['servicio']}: ${servicio['costo']:.2f}")
            print(f"Monto total: ${nota['monto_total']:.2f}")
            if nota['cancelada']:
                print("Estado: Cancelada")
            else:
                print("Estado: Activa")
        else:
            print("La nota no existe o está cancelada.")
    except ValueError:
        print("Error: Ingrese un folio válido (número entero).")
    except Exception :
        print(f"Ocurrió un error inesperado: ")

#consultar notas por período
def consultar_por_periodo():
    try:
        fecha_inicial = input("Ingrese la fecha inicial (YYYY-MM-DD) o presione Enter para usar 2000-01-01: ")
        if fecha_inicial == "":
            fecha_inicial = datetime.datetime(2000, 1, 1)
        else:
            fecha_inicial = datetime.datetime.strptime(fecha_inicial, "%Y-%m-%d")

        fecha_final = input("Ingrese la fecha final (YYYY-MM-DD) o presione Enter para usar la fecha actual: ")
        if fecha_final == "":
            fecha_final = datetime.datetime.now()
        else:
            fecha_final = datetime.datetime.strptime(fecha_final, "%Y-%m-%d")

        if fecha_final < fecha_inicial:
            print("Error: La fecha final no puede ser anterior a la fecha inicial.")
            return

        notas_periodo = {}
        monto_promedio = 0
        contador_notas = 0

        for folio, nota in notas.items():
            if fecha_inicial <= nota["fecha"] <= fecha_final:
                notas_periodo[folio] = nota
                monto_promedio += nota["monto_total"]
                contador_notas += 1

        if contador_notas > 0:
            monto_promedio /= contador_notas
            print(f"Resultados para el período de {fecha_inicial.strftime('%Y-%m-%d')} a {fecha_final.strftime('%Y-%m-%d')}:")
            print(f"Cantidad de notas encontradas: {contador_notas}")
            print(f"Monto promedio de las notas: ${monto_promedio:.2f}")
        else:
            print("No se encontraron notas en el período especificado.")

    except ValueError:
        print("Error: Ingrese fechas válidas (YYYY-MM-DD).")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

#cancelar una nota
def cancelar_nota():
    try:
        folio = int(input("Ingrese el folio de la nota a cancelar: "))
        if folio in notas:
            nota = notas[folio]
            if not nota["cancelada"]:
                nota["cancelada"] = True
                print(f"Nota con folio {folio} cancelada con éxito.")
            else:
                print("La nota ya está cancelada.")
        else:
            print("La nota no existe en el sistema.")
    except ValueError:
        print("Error: Ingrese un folio válido (número entero).")
    except Exception as e:
        print(f"Ocurrió un error inesperado:")

#recuperar una nota cancelada
def recuperar_nota():
    try:
        notas_canceladas = [folio for folio, nota in notas.items() if nota["cancelada"]]
        if notas_canceladas:
            print("Notas canceladas:")
            for folio in notas_canceladas:
                print(f"Folio: {folio}")
            folio_recuperar = int(input("Ingrese el folio de la nota que desea recuperar: "))
            if folio_recuperar in notas:
                nota = notas[folio_recuperar]
                if nota["cancelada"]:
                    nota["cancelada"] = False
                    print(f"Nota con folio {folio_recuperar} recuperada con éxito.")
                else:
                    print("La nota no está cancelada.")
            else:
                print("La nota no existe en el sistema.")
        else:
            print("No hay notas canceladas para recuperar.")
    except ValueError:
        print("Error: Ingrese un folio válido (número entero).")
    except Exception as e:
        print(f"Ocurrió un error inesperado:")

# Menú
while True:
    print("\nMenú Principal:")
    print("1. Registrar una nota")
    print("2. Consultar nota por folio")
    print("3. Consultar notas por período")
    print("4. Cancelar una nota")
    print("5. Recuperar una nota cancelada")
    print("6. Salir")

    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        registrar_nota()
    elif opcion == "2":
        consultar_por_folio()
    elif opcion == "3":
        consultar_por_periodo()
    elif opcion == "4":
        cancelar_nota()
    elif opcion == "5":
        recuperar_nota()
    elif opcion == "6":
        guardar_datos_csv()  
        print("Saliendo del programa...")
        break
    else:
        print("Opción no válida. Por favor, seleccione una opción válida.")