import numpy as np
from red_hospitalaria import Red_Salud, Paciente, Lista_Pacientes
from modelo_optimizacion import HospitalNetwork


# Funcion que simula la llegada de pacientes
def patient_arrival():

    # LLegada por GRD
    mu, sigma = 50.3, 7.2

    lista_grds = []
    cantidad_pacientes = 0

    for i in range(10):
        s = max(1, np.random.normal(mu, sigma))
        s = int(s)
        lista_grds.append(s)
        cantidad_pacientes += s

    # LLegada por Hospital
    # Para el Hospital Barros Luco Trudeau
    mu_1, sigma_1 = 187.4, 19
    s_1 = max(1, np.random.normal(mu_1, sigma_1))
    s_1 = int(s_1)
    # Para el Hospital de Enfermedades Infecciosas Dr. Lucio Córdova,
    # Hospital El Pino y Hospital Parroquial de San Bernardo
    mu_2, sigma_2 = 61.9, 8.7
    s_2a = max(1, np.random.normal(mu_2, sigma_2))
    s_2b = max(1, np.random.normal(mu_2, sigma_2))
    s_2c = max(1, np.random.normal(mu_2, sigma_2))
    s_2a = int(s_2a)
    s_2b = int(s_2b)
    s_2c = int(s_2c)
    # Para el Hospital Dr. Exequiel González Cortés
    mu_3, sigma_3 = 126.5, 13.3
    s_3 = max(1, np.random.normal(mu_3, sigma_3))
    s_3 = int(s_3)

    cantidad_pacientes_proporcion = s_1 + s_2a + s_2b + s_2c + s_3

    lista_grds_1 = []
    lista_grds_2 = []
    lista_grds_3 = []
    lista_grds_4 = []
    lista_grds_5 = []
    for i in range(10):
        lista_grds_1.append(int(lista_grds[i] * s_1 / cantidad_pacientes_proporcion))
        lista_grds_2.append(int(lista_grds[i] * s_2a / cantidad_pacientes_proporcion))
        lista_grds_4.append(int(lista_grds[i] * s_2b / cantidad_pacientes_proporcion))
        lista_grds_5.append(int(lista_grds[i] * s_2c / cantidad_pacientes_proporcion))
        lista_grds_3.append(int(lista_grds[i] * s_3 / cantidad_pacientes_proporcion))

    lista_grds_final = [
        lista_grds_1,
        lista_grds_2,
        lista_grds_3,
        lista_grds_4,
        lista_grds_5,
    ]

    lista_pacientes_del_dia = []

    num_hospital = 0
    for grd_hospital in lista_grds_final:
        num_grd = 0
        for numero_pacientes_por_grd in grd_hospital:
            for i in range(numero_pacientes_por_grd):
                paciente = Paciente(num_grd, num_hospital)
                lista_pacientes_del_dia.append(paciente)

            num_grd += 1

        num_hospital += 1

    return lista_pacientes_del_dia


###======================================= Generar Red de Hospitales

health_network = Red_Salud()

health_network.add_hospital(
    "Hospital Barros Luco Trudeau",
    10,
    12,
    {
        "coronario": 3,
        "hepatico": 2,
        "respiratorio": 3,
        "renal": 2,
        "neurologico": 3,
        "traumatologico": 4,
        "esofagico": 3,
        "oftalmologico": 2,
        "circulatorio": 1,
        "intestinal": 3,
    },
    6,
    18,
    42,
    16,
)

health_network.add_hospital(
    "Hospital de Enfermedades Infecciosas Dr. Lucio Córdova",
    5,
    12,
    {
        "coronario": 2,
        "hepatico": 2,
        "respiratorio": 3,
        "renal": 2,
        "neurologico": 1,
        "traumatologico": 2,
        "esofagico": 3,
        "oftalmologico": 2,
        "circulatorio": 2,
        "intestinal": 2,
    },
    4,
    9,
    18,
    8,
)

health_network.add_hospital(
    "Hospital Dr. Exequiel González Cortés",
    7,
    12,
    {
        "coronario": 2,
        "hepatico": 1,
        "respiratorio": 2,
        "renal": 1,
        "neurologico": 1,
        "traumatologico": 3,
        "esofagico": 3,
        "oftalmologico": 3,
        "circulatorio": 2,
        "intestinal": 1,
    },
    4,
    12,
    25,
    12,
)

health_network.add_hospital(
    "Hospital El Pino",
    4,
    10,
    {
        "coronario": 1,
        "hepatico": 1,
        "respiratorio": 2,
        "renal": 2,
        "neurologico": 1,
        "traumatologico": 2,
        "esofagico": 1,
        "oftalmologico": 2,
        "circulatorio": 1,
        "intestinal": 1,
    },
    2,
    5,
    15,
    4,
)

health_network.add_hospital(
    "Hospital Parroquial de San Bernardo",
    3,
    10,
    {
        "coronario": 1,
        "hepatico": 1,
        "respiratorio": 1,
        "renal": 1,
        "neurologico": 2,
        "traumatologico": 1,
        "esofagico": 2,
        "oftalmologico": 2,
        "circulatorio": 1,
        "intestinal": 1,
    },
    2,
    5,
    10,
    4,
)

###======================================= Generar Simulacion

weeks = 1
simulation_days = 7 * weeks

for week in range(weeks):

    for day in range(simulation_days):

        health_network.patient_list.extender_lista_pacientes(patient_arrival())

        today = (day + 1) % 7

        # llegada de pacientes

    health_network.patient_list.estadistica()

    health_network.patient_list.exportar_lista_pacientes()  ## ACA SE GENERA EL ARCHIVO lista_pacientes.json que es el que lee tu programa

    ##===================================================  EJECUTAR Programación

    HN = HospitalNetwork("lista_pacientes.json", "resultado_optimizacion", gap=0.3)
    # HN.start()
    HN.run()

    ##===================================================  FINALIZAR Programación |||| Tu programa debe entregar como output el resultado_optimizacion.json que es el que lee la funcion que esta en la linea de abajo

    health_network.procesar_programacion()
