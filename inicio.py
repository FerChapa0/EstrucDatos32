import datetime
import time
fecha_actual = datetime.date.today()
print("Evidencia 1 prueba")
#Metodos


#Menu
registros=[]
TALLER_MECANICO={
    "NOTAS":{
        1:{
            "FECHA":"x",
            "CLIENTE":"x",
            "MONTO":"x",
            "DETALLES":[{}]
        }
    }
}
folio=0
while True:
    print("Taller Mecanico")
    print("1.Registrar una nota\n2.Consultas y Reportes\n3.Cancelar una nota\n4.Recuperar nota\n5.Salir del sistema")
    op=int(input("Eliga una opcion del menu: "))
    if op==5:
        break
    if op==1:
        folio=+1

        nomcliente=input("Cual es su nombre: ")
        fecha=input("Cual es su fecha: ")
        while True:
            descripcion=input("Cual es su servicio: (deje en blanco para terminar)")
            if descripcion=="":
                break
            monto=float(input("Cual es su monto a pagar: "))
            datos =((nomcliente,fecha,descripcion,monto))
            TALLER_MECANICO={folio:datos}
            print(TALLER_MECANICO)

    if op==2:
        while True:    
            print("Opciones: \n1.Consulta por periodo \n2.Consulta por folio")
            consulta=int(input("Eliga una opcion: "))
            if consulta==1:
                consulta_periodo=input("Cual es su periodo")
                break
            elif consulta==2:
                consulta_folio=int(input("Cual es su folio"))
                while True:
                    if consulta_folio in TALLER_MECANICO:
                        TALLER_MECANICO.pop
                    else:        
                        print("folio no valido intente de nuevo")
                        break
                break
            if consulta <1 or consulta>2:
                print("opcion invalida, intente de nuevo")
                continue
    if op==3:
            print("Cancelar la nota")
            consulta_folio=int(input("Cual es su folio"))
            while True:
                if consulta_folio in TALLER_MECANICO:
                    print("folio no valido intente de nuevo")
                    break
    if op==4:
        pass
    if op==5:
        break
        #monto a pagar 