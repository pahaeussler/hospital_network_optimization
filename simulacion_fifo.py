from constantes import *
from random import *

## Persona (id, grd, hosítal_llegada, deadline)

hospitals = {
    "Hospital Barros Luco Trudeau": 0,
    "Hospital de Enfermedades Infecciosas Dr. Lucio Córdova": 1,
    "Hospital Dr. Exequiel González Cortés": 2,
    "Hospital El Pino": 3,
    "Hospital Parroquial de San Bernardo": 4,
}


def replace_indices(ide, day, hospital, grd, dead_line):
    ide = int(ide)
    hospital = hospitals[hospital.replace("\xa0", "")]
    grd = int(grd.replace("GRD", "")) - 1
    dead_line = int(dead_line)
    return int(ide), grd, int(day), hospital, dead_line


def open_datos(name_file, end=None):
    end = end if end is not None else 9999999999
    with open(name_file, "r", encoding="UTF-8") as file:
        header = ["day", "hospital", "grd", "dead_line"]
        next(file)
        lista = []
        for i, line in enumerate(file):
            if i >= end:
                break
            line = line.strip().split(",")
            lista.append(replace_indices(*line))
        return lista


def crear_pacientes(lista):
    pacientes = []
    for i in lista:
        pacientes.append(Patience(i[0], i[1], i[2], i[3], i[4]))
    return pacientes


class Patience:
    def __init__(self, id, grd, arrival_time, hospital, dead_line):
        self.id = id
        self.grd = grd
        self.arrival_time = arrival_time
        self.hospital = hospital
        self.dead_line = dead_line
        self.asignado = False

    def __repr__(self):
        return f"ide: {self.id}, grd: {self.grd}, hospital: {self.hospital}, dead_line: {self.dead_line}"


def hay_personal(grd, disponible):
    respuesta = True
    for m in range(m_max):
        if disponible[m] - P[m, grd] < 0:
            respuesta = False
    return respuesta


def calcular_costos(asignaciones, lista_pacientes):
    suma = 0
    for i in asignaciones:
        suma += CO[i[3]]
    for j in lista_pacientes:
        if not j.asignado:
            suma += C[j.hospital]
    return suma


# X[j, t, h, q, g]


def asignar_pacientes(lista_pacientes):
    Asignaciones = []
    nueva_lista = lista_pacientes
    for t in range(t_max):
        personal_disponible = {}
        for m in range(m_max):
            personal_disponible[m] = PD[m]
        randomizar = [(c, v) for c in range(h_max) for v in range(CQ[c])]
        shuffle(randomizar)
        for h, q in randomizar:
            aux_grd = None
            suma = 0
            for i in nueva_lista:
                if i.hospital == h and not i.asignado and i.dead_line >= t:
                    if aux_grd is None and hay_personal(i.grd, personal_disponible):
                        aux_grd = i.grd
                        suma += D[i.grd]
                        Asignaciones.append((i.id + 1, t, h, q))
                        i.asignado = True
                        for m in range(m_max):
                            personal_disponible[m] = (
                                personal_disponible[m] - P[m, aux_grd]
                            )
                    else:
                        if i.grd == aux_grd:
                            if D[i.grd] + suma <= H[h]:
                                suma += D[i.grd]
                                Asignaciones.append((i.id + 1, t, h, q, i.grd))
                                i.asignado = True
                            else:
                                break
    return (
        len(nueva_lista),
        len([c for c in nueva_lista if c.asignado == True]),
        len([c for c in nueva_lista if c.asignado == False]),
        calcular_costos(Asignaciones, nueva_lista),
    )


# return "De {} pacientes se asignan:{} y se dejan {}, esto nos entrega un costo de ${}".format(len(nueva_lista),
#                                                             len([c for c in nueva_lista if c.asignado == True]),
#                                                             len([c for c in nueva_lista if c.asignado == False]),
#                                                                                               calcular_costos(Asignaciones,
#                                                                                                               nueva_lista))


if __name__ == "__main__":
    x = open_datos("datos.csv")
    datos = []
    for i in range(100):
        y = crear_pacientes(x)
        z = asignar_pacientes(y)
        datos.append(z)
        print(z)
    suma = 0
    suma2 = 0
    for i in range(len(datos) - 1):
        suma += datos[i][1]
        suma2 += datos[i][3]
    print("Promedio de 100 simulaciones:")
    print("Pacientes Atendidos = {}, Costo = {}".format(suma / 100, suma2 / 100))
    print("Pacientes enviados a clinica privada: {}".format(36975 - suma / 100))
