import numpy as np
import collections
import json

###======================================= CLases


class Hospital:
    id_hospital = 0

    def __init__(
        self,
        nombre_hospital,
        quirofanos,
        horas_quirofano,
        especialistas,
        anestesistas,
        medicos_apoyo,
        enfermeras,
        arsenaleros,
    ):
        self._id = Hospital.id_hospital
        Hospital.id_hospital += 1

        # nombre hospital (string)
        self.nombre_hospital = nombre_hospital
        # numero de quirofanos (int)
        self.quirofanos = quirofanos
        # horas de disponibilidad de los quirofanos para cada hospital (int)
        self.horas_quirofano = horas_quirofano

        # a continuacion, el personal del hospital se guarda en la posicion 0 y
        # el personal que viene o se va en la posicion 1 (puede ser negativo)

        # cantidad de medicos especialistas por cada hospital (dic:int)
        self.especialistas = [
            especialistas,
            {
                "coronario": 0,
                "hepatico": 0,
                "respiratorio": 0,
                "renal": 0,
                "neurologico": 0,
                "traumatologico": 0,
                "esofagico": 0,
                "oftalmologico": 0,
                "circulatorio": 0,
                "intestinal": 0,
            },
        ]
        # numero de anestesistas por hospital
        self.anestesistas = [anestesistas, 0]
        # numero de medicos de apoyo por hospital
        self.medicos_apoyo = [medicos_apoyo, 0]
        # numero de enfermeras por hospital
        self.enfermeras = [enfermeras, 0]
        # numero de arsenaleros por hospital
        self.arsenaleros = [arsenaleros, 0]


class EquipoMedico:
    def __init__(self):
        pass

    def evaluarPaciente(self, grd):
        tiempo = 0

        if grd == 0:
            tiempo = np.random.random_integers(5, 9)

        elif grd == 1:
            tiempo = np.random.random_integers(2, 5)

        elif grd == 2:
            tiempo = round(np.random.triangular(2, 5, 7))

        elif grd == 3:
            tiempo = np.random.random_integers(1, 3)

        elif grd == 4:
            tiempo = round(np.random.triangular(3, 4, 6))

        elif grd == 5:
            tiempo = np.random.random_integers(1, 5)

        elif grd == 6:
            tiempo = round(np.random.triangular(1, 2, 4))

        elif grd == 7:
            tiempo = round(np.random.triangular(1, 3, 4))

        elif grd == 8:
            tiempo = round(np.random.triangular(2, 3, 6))

        elif grd == 9:
            tiempo = np.random.random_integers(2, 5)

        tiempo = int(tiempo)

        return tiempo


class Red_Salud:
    def __init__(self):
        self.hospitales = {}
        self.patient_list = Lista_Pacientes()
        self.equipo_medico = EquipoMedico()
        self.costo_traslado_clinica = 0
        self.costo_operaciones_clinica = 0
        self.cantidad_operaciones = {"fallidas": 0, "realizadas": 0}

    def add_hospital(
        self,
        nombre_hospital,
        quirofanos,
        horas_quirofano,
        especialistas,
        anestesistas,
        medicos_apoyo,
        enfermeras,
        arsenaleros,
    ):
        new_hospital = Hospital(
            nombre_hospital,
            quirofanos,
            horas_quirofano,
            especialistas,
            anestesistas,
            medicos_apoyo,
            enfermeras,
            arsenaleros,
        )
        self.hospitales[new_hospital._id] = new_hospital

    def procesar_programacion(self):
        data_programacion = ""

        with open("resultado_optimizacion.json") as fp:
            data_programacion = json.load(fp)

        x, w = self.pacientesAProgramar(data_programacion)

        no_programados = self.pacientesNoConsiderados(x, w)

        ##======================= Diccionario de pacientes en quirofano en hospital para un dia

        pacientes_por_quirofano_hospital_dia = {}

        for dia in range(5):
            pacientes_por_quirofano_hospital_dia[dia] = {}

            for hospital in range(5):
                pacientes_por_quirofano_hospital_dia[dia][hospital] = {}
                lista_quirofanos_hospital = []
                for paciente_data in data_programacion["X"]:
                    if (
                        paciente_data["dia"] == dia
                        and paciente_data["hospital"] == hospital
                    ):
                        lista_quirofanos_hospital.append(paciente_data["quirofano"])

                for quirofano in lista_quirofanos_hospital:
                    pacientes_por_quirofano_hospital_dia[dia][hospital][quirofano] = []

        for paciente_data in data_programacion["X"]:
            pacientes_por_quirofano_hospital_dia[paciente_data["dia"]][
                paciente_data["hospital"]
            ][paciente_data["quirofano"]].append(paciente_data)

        ##=========================== FIN

        ##=========================== Asignacion tiempo de medicos

        lista_tiempos_pacientes = []

        for dia in range(5):
            for hospital in range(5):
                for quirofano in range(10):
                    if quirofano in pacientes_por_quirofano_hospital_dia[dia][hospital]:
                        tiempos_pacientes = []

                        for paciente in pacientes_por_quirofano_hospital_dia[dia][
                            hospital
                        ][quirofano]:
                            tiempos_pacientes.append(
                                [
                                    paciente["paciente"],
                                    self.equipo_medico.evaluarPaciente(paciente["GRD"]),
                                ]
                            )

                        lista_tiempos_pacientes.append([hospital, tiempos_pacientes])

        ##=========================== FIN

        ##=========================== Evaluar si alcanzan a operar

        horas_atencion = {0: 12, 1: 12, 2: 12, 3: 10, 4: 10}

        for quirofano in lista_tiempos_pacientes:
            tiempo_quirofano_actual = horas_atencion[quirofano[0]]
            a_operar, a_clinica = self.ajustarQuirofano(
                quirofano[1], tiempo_quirofano_actual
            )

            self.cantidad_operaciones["realizadas"] += len(a_operar)
            self.cantidad_operaciones["fallidas"] += len(a_clinica)

            w.extend(a_clinica)

            for id_operar in a_clinica:
                x.remove(id_operar)

        costos_traslado = {0: 0.33, 1: 0.28, 2: 0.25, 3: 0.2, 4: 0.32}
        costos_operacion = {
            0: 11.4,
            1: 6.4,
            2: 6.85,
            3: 5.1,
            4: 8.65,
            5: 3.26,
            6: 2.59,
            7: 1.2,
            8: 4.5,
            9: 3.56,
        }

        for id_paciente in w:

            for paciente in self.patient_list.pacientes:
                if id_paciente == paciente._id:
                    self.costo_traslado_clinica += costos_traslado[
                        paciente.arrival_hospital
                    ]
                    self.costo_operaciones_clinica += costos_operacion[paciente.grd]

        print(
            "Pacientes que se iban a operar pero fueron trasladados por falta de tiempo: ",
            self.cantidad_operaciones["fallidas"],
        )
        print(
            "Pacientes que se agregaron lista espera proxima semana: ",
            len(no_programados),
        )
        print("Paccientes trasladados a clinica: ", len(w))
        print(
            "Costos totales sin fase 1: ",
            self.costo_traslado_clinica + self.costo_operaciones_clinica,
        )

    def ajustarQuirofano(self, pacientes_quirofano, hora):
        lista_operar = []
        lista_clinica = []
        suma_horas = 0

        for paciente in pacientes_quirofano:
            suma_horas += paciente[1]

        if suma_horas > hora:
            tope = len(pacientes_quirofano)

            while suma_horas > hora and tope >= 0:
                suma_horas = 0

                lista_clinica.append(pacientes_quirofano[tope - 1][0])

                for i in range(tope):
                    suma_horas += pacientes_quirofano[i][1]

                tope -= 1

            if tope >= 0:
                for i in range(tope + 1):
                    lista_operar.append(pacientes_quirofano[i][0])

        else:
            for paciente in pacientes_quirofano:
                lista_operar.append(paciente[0])

        return lista_operar, lista_clinica

    def pacientesAProgramar(self, data):
        id_x = []
        id_w = []

        for asignacion_x in data["X"]:
            id_x.append(asignacion_x["paciente"])

        for asignacion_w in data["W"]:
            id_w.append(asignacion_w["paciente"])

        return id_x, id_w

    def pacientesNoConsiderados(self, x, w):
        pacientes_no_considerados = []

        for paciente in self.patient_list.pacientes:
            if paciente._id in x or paciente._id in w:
                pass
            else:
                pacientes_no_considerados.append(paciente._id)

        return pacientes_no_considerados


class Paciente:
    id_paciente = 0

    def __init__(self, GRD, hospital_llegada):
        self._id = Paciente.id_paciente
        Paciente.id_paciente += 1

        self.grd = GRD
        self.arrival_hospital = hospital_llegada
        self.send_hospital = ""
        self.dead_line = self.deadLine()
        self.traslado_hospital = False
        self.traslado_clinica = False
        self.asignado_quirofano = False

    def to_dict(self):
        return {
            "ide": self._id,
            "grd": self.grd,
            "hospital": self.arrival_hospital,
            "dead_line": self.dead_line,
        }

    def deadLine(self):
        dead_line = 0

        if self.grd == 0:
            if np.random.uniform() < 0.91:
                dead_line = np.random.random_integers(1, 2)
            else:
                dead_line = 0

        elif self.grd == 1:
            if np.random.uniform() < 0.96:
                dead_line = np.random.random_integers(1, 4)
            else:
                dead_line = 5

        elif self.grd == 2:
            if np.random.uniform() < 0.84:
                dead_line = np.random.random_integers(2, 6)
            else:
                if np.random.uniform() < 0.5:
                    dead_line = 1
                else:
                    dead_line = 7

        elif self.grd == 3:
            if np.random.uniform() < 0.976:
                dead_line = np.random.random_integers(2, 9)
            else:
                dead_line = 1

        elif self.grd == 4:
            if np.random.uniform() < 0.985:
                dead_line = np.random.random_integers(2, 11)
            else:
                dead_line = 12

        elif self.grd == 5:
            if np.random.uniform() < 0.91:
                dead_line = np.random.random_integers(3, 13)
            else:
                if np.random.uniform() < 0.5:
                    dead_line = 2
                else:
                    dead_line = 14

        elif self.grd == 6:
            if np.random.uniform() < 0.985:
                dead_line = np.random.random_integers(3, 16)
            else:
                dead_line = 2

        elif self.grd == 7:
            if np.random.uniform() < 0.989:
                dead_line = np.random.random_integers(3, 18)
            else:
                dead_line = 19

        elif self.grd == 8:
            if np.random.uniform() < 0.945:
                dead_line = np.random.random_integers(4, 20)
            else:
                if np.random.uniform() < 0.5:
                    dead_line = 3
                else:
                    dead_line = 21

        elif self.grd == 9:
            if np.random.uniform() < 0.991:
                dead_line = np.random.random_integers(4, 23)
            else:
                dead_line = 3

        return int(dead_line)

    def __str__(self):
        return "id:{} | grd:{} | arrival_hospital:{} | dead_line:{}".format(
            self._id, self.grd, self.arrival_hospital, self.dead_line
        )

    def __repr__(self):
        return "id:{} | grd:{} | arrival_hospital:{} | dead_line:{}".format(
            self._id, self.grd, self.arrival_hospital, self.dead_line
        )


class Lista_Pacientes:
    def __init__(self):
        self.pacientes = []

    def extender_lista_pacientes(self, lista_importada):
        self.pacientes.extend(lista_importada)

    def exportar_lista_pacientes(self):
        data = []

        for paciente in self.pacientes:
            data.append(paciente.to_dict())

        with open("lista_pacientes.json", "w") as fp:
            json.dump(data, fp)

    def cantidad_pacientes(self):
        return len(self.pacientes)

    def cantidad_pacientes_estadistica(self):
        lista_grds = []
        lista_hospitales = []
        for paciente in self.pacientes:
            lista_grds.append(paciente.grd)
            lista_hospitales.append(paciente.arrival_hospital)

        counter_grd = collections.Counter(lista_grds)
        counter_hospital = collections.Counter(lista_hospitales)

        return counter_grd, counter_hospital

    def estadistica(self):
        print("Cantidad de pacientes: {}".format(self.cantidad_pacientes()))
        # print('Cantidad de pacientes por GRD:')
        # for i in range(10):
        #     print('GRD {}: {}'.format(i+1,self.cantidad_pacientes_estadistica()[0][i]))
        #
        # for i in range(5):
        #     print('Hospital {}: {}'.format(i+1,self.cantidad_pacientes_estadistica()[1][i]))

    def __str__(self):
        return "{}".format(self.pacientes)

    def __repr__(self):
        return "{}".format(self.pacientes)
