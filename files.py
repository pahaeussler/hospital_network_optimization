from parameters import D, CO, PD
import json

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


def fase_1(name_file, cut, end=3500):
    datos = open_datos(name_file, end)
    new_list = sorted(datos, key=lambda lista: D[lista[3]] / CO[lista[3]])
    # j = (min(PD.values())*max(H.values())//min(D.values()))*5 maximos a anlizar por semana
    return new_list[:cut], new_list[cut:]


def open_json(name_file):
    with open(name_file, "r") as fp:
        return json.load(fp)


if __name__ == "__main__":
    buenos = fase_1("Archivos/" + "Datos.csv", 3500)
    # print(buenos)
