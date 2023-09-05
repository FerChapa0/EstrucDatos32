import datetime
import time
fecha_actual = datetime.date.today()
#Metodos
#Menu
registros=[]
resultado=[]
borrados={}
datos=()
TALLER_MECANICO={}
folio=0
while True:
    print("Taller Mecanico")
    print("1.Registrar una nota\n2.Consultas y Reportes\n3.Cancelar una nota\n4.Recuperar nota\n5.Salir del sistema")
    op=int(input("Eliga una opcion del menu: "))
    if op==5:
        break
    if op==1:
        folio+=1
        nomcliente=input("Cual es su nombre: ")
        fecha=input("Cual es su fecha: (dd/mm/aaaa)")
        descripcion=input("Cual es su servicio: (deje en blanco para terminar)")
        monto=float(input("Cual es su monto a pagar: "))
        TALLER_MECANICO[folio]=(nomcliente,fecha,descripcion,monto)
        print(TALLER_MECANICO)

    if op==2:
        while True:    
            print("Opciones: \n1.Consulta por periodo \n2.Consulta por folio")
            consulta=int(input("Eliga una opcion: "))
            if consulta==1:
                consulta_periodo=input("Cual es su periodo:")
                fechanueva=datetime.datetime.strptime(consulta_periodo, "%d/%m/%Y").date()
                if fechanueva<=fecha_actual:
                    for folio,datos in TALLER_MECANICO.items():
                        if datos[2]==consulta_periodo:
                            resultado.append(datos)
                            print(f'El registro es: {TALLER_MECANICO.values()}')
            elif consulta==2:
                consulta_folio=int(input("Cual es su folio: "))
                try:
                    for folio in TALLER_MECANICO:
                        print(f'El registro es: {TALLER_MECANICO.values()}')
                except ValueError:        
                        print("folio no valido intente de nuevo")
                        break
            if consulta <1 or consulta>2:
                print("opcion invalida, intente de nuevo")
                continue
    if op==3:
            print("Cancelar la nota")
            consulta_folio=int(input("Cual es su folio"))
            try:
                for folio in TALLER_MECANICO:
                        print(f'El registro es: {TALLER_MECANICO.values()}')

                confirmacion=int(input("Desea confirmar la accion(1=si/2=no): "))
                if confirmacion==1:
                     borrados[folio+1]=(folio+1,nomcliente,fecha,descripcion,monto)
                     TALLER_MECANICO.pop(consulta_folio)
                     print("Se ha borrado un elemento")
                     print(TALLER_MECANICO)
            except ValueError:        
                        print("Error tipo de dato intente de nuevo")
                        break
    if op==4:
        print("Recuperar nota")
        print(f'Notas recuperadas\n')
        print(f'Folio\tNombre Cliente\tFecha\tMonto')
        print(f'\t{borrados.values()}')
        recup=int(input("Cual nota desea recuperar:"))
        for recup in borrados:
             input(f'El detalle de la nota es: ')
             print(f'dato a recuperar: {borrados.values()}')
        
        conrepu=int(input('Desea confirmar recuperar esta nota:(1=si/2=no)'))
        if conrepu==1:
            TALLER_MECANICO[TALLER_MECANICO.keys+1]=borrados.values
            print(TALLER_MECANICO)
        else:
            print("Se cancelo la recuperacion")
            continue
    

