import threading
from gurobipy import *
from parameters import *
import time
import json
from fase_1_optimizacion import Red

# Y[g, t, h, q]
# X[j, t, h, q]
# W[j, t]
# Z[m, h, q, t]
# B[h1, h2, m, t]
# T[j, HLL, h2]
# Hl[j, HLL]


class HospitalNetwork(threading.Thread):
    lock = threading.Lock()
    best_solution = 9999999999
    """Optimizar los hospitales"""

    def __init__(self, path, save_name="Resultados", gap=0.05):
        super().__init__()
        self.red = Red(path)
        self.n_week = self.red.n_week
        self.jgthd = self.red.selected_patiences_jgthd
        self.Y = self.red.quirofano_repartition()
        self.save_name = save_name
        print("Pacientes a analizar: ", len(self.jgthd))
        print("Quirofanos a Utilizar:", len(self.Y))
        self.gap = gap
        self.model = Model("Quirofanos")

    def generate_lists(self):
        lx = list()
        lw = list()
        lz = list()
        lb = list()
        lt = list()
        lhl = list()
        for j, g, TLL, HLL, dead_line in self.jgthd:
            for t in range(dead_line):
                for h in range(h_max):
                    for q in range(CQ[h]):
                        lx.append((j, t, h, q))
            lw.append(j)
            for h2 in range(h_max):
                if HLL != h2:
                    lt.append((j, HLL, h2))
            lhl.append((j, HLL))

        for t in range(t_max):
            for m in range(m_max):
                for h in range(h_max):
                    for q in range(CQ[h]):
                        lz.append((m, h, q, t))
                    for h2 in range(h_max):
                        if h != h2:
                            lb.append((h, h2, m, t))

        return lx, lw, lz, lt, lb, lhl

    def generate_vars(self):
        start_time = time.time()
        lx, lw, lz, lt, lb, lhl = self.generate_lists()
        self.X = self.model.addVars(lx, vtype=GRB.BINARY, name="X")
        self.W = self.model.addVars(lw, vtype=GRB.BINARY, name="W")
        self.Z = self.model.addVars(lz, vtype="N", name="Z")
        self.T = self.model.addVars(lt, vtype=GRB.BINARY, name="T")
        self.B = self.model.addVars(lb, vtype="N", name="B")
        self.HL = {k: 1 for k in lhl}
        finished_time = time.time()
        print("Tiempo de generar variables:", finished_time - start_time)

    def atender_al_paciente_en_su_tiempo_limite(self):  # Check
        for j, g, TLL, HLL, dead_line in self.jgthd:
            suma = 0
            for t in range(min(dead_line, t_max)):
                suma = self.X.sum(j, t, "*", "*")
            suma += self.W[j]
            if suma:
                self.model.addConstr(
                    suma == 1, "Atender al paciente en su tiempo límite"
                )

    def personal_medico_necesario_en_el_hospital(self):
        for t in range(t_max):
            for h in range(h_max):
                for q in range(CQ[h]):
                    for m in range(m_max):
                        # self.model.addConstr(
                        #                     self.X[j, t, h, q]*P[m, g] <= self.Z[m, h, q, t],
                        #                     "Personal médico necesario en el hospital")
                        #     suma_y = 0
                        #     for g in range(g_max):
                        #         suma_y += self.Y[g, t, h, q]
                        self.model.addConstr(
                            self.Y.sum("*", t, h, q) * P[m, g] <= self.Z[m, h, q, t],
                            "Personal médico necesario en el hospital",
                        )

    def no_sobrepasar_personal_medico_disponible(self):
        for t in range(t_max):
            for m in range(m_max):
                # Z[m, h, q, t]
                self.model.addConstr(
                    self.Z.sum(m, "*", "*", t) <= PD[m],
                    "No sobrepasar personal médico disponible",
                )

    def calibración_de_personal(self):
        for h in range(h_max):
            for m in range(m_max):
                for t in range(t_max):
                    # Z[m, h, q, t]
                    # B[h1, h2, m, t]
                    self.model.addConstr(
                        self.Z.sum(m, h, "*", t) - Z0[m, h] == self.B.sum(h, "*", m, t),
                        "Calibración de personal",
                    )
                    t_last = t

    def no_sobrepasar_el_tiempo_disponible_del_quirofano(self):
        for t in range(t_max):
            for h in range(h_max):
                for q in range(CQ[h]):
                    self.model.addConstr(
                        quicksum(
                            self.X[j, t, h, q] * D[g] if (j, t, h, q) in self.X else 0
                            for j, g, TLL, HLL, dead_line in self.jgthd
                        )
                        <= H[h],
                        "No sobrepasar el tiempo disponible del quirófano",
                    )

    def atender_y_usar_el_quirofano_solo_si_se_esta_atendiendo_a_ese_GRD(self):
        for j, g, TLL, HLL, dead_line in self.jgthd:
            for m in range(m_max):
                for t in range(min(t_max, dead_line)):
                    for h in range(h_max):
                        for q in range(CQ[h]):
                            self.model.addConstr(
                                self.X[j, t, h, q] * P[m, g] <= self.Z[m, h, q, t],
                                "Atender y usar el quirófano sólo si se está atendiendo a ese GRD",
                            )

    def calibracion_traslado_de_pacientes(self):
        for j, g, TLL, HLL, dead_line in self.jgthd:
            for h2 in range(h_max):
                for q in range(CQ[h2]):
                    suma = 0
                    for t in range(min(t_max, dead_line)):
                        if HLL != h2:
                            suma += self.X[j, t, h2, q]
                    if suma and HLL != h2:
                        self.model.addConstr(
                            self.T[j, HLL, h2] == suma * self.HL[j, HLL],
                            "Calibración traslado de pacientes",
                        )

    def generate_restrictions(self):
        start_time = time.time()
        self.atender_al_paciente_en_su_tiempo_limite()
        # self.maximo_de_dos_GRD_por_quirofano_al_dia()
        # self.personal_medico_necesario_en_el_hospital()
        self.no_sobrepasar_personal_medico_disponible()
        # self.calibración_de_personal()
        self.no_sobrepasar_el_tiempo_disponible_del_quirofano()
        self.atender_y_usar_el_quirofano_solo_si_se_esta_atendiendo_a_ese_GRD()
        self.calibracion_traslado_de_pacientes()
        # self.model.Params.timeLimit = 360
        self.model.Params.MIPGap = self.gap
        finished_time = time.time()
        print("Tiempo de generar restricciones:", finished_time - start_time)

    def set_objetive(self):
        # FUNCION OBJETIVO
        start_time = time.time()
        obj = 0
        for j, GLL, TLL, HLL, dead_line in self.jgthd:
            obj += self.W[j] * (C[HLL] + CO[GLL])
            for h2 in range(h_max):
                if HLL != h2:
                    obj += self.T[j, HLL, h2] * CP[HLL, h2]
        for t in range(t_max):
            for h1 in range(h_max):
                for h2 in range(h_max):
                    for m in range(m_max):
                        if h1 != h2:
                            obj += self.B[h1, h2, m, t] * CM[h1, h2]
        finished_time = time.time()
        self.model.setObjective(obj, GRB.MINIMIZE)
        print("Tiempo de generar funcion objetivo:", finished_time - start_time)

    def optimize_model(self):
        start_time = time.time()
        self.model.optimize()
        finished_time = time.time()
        print("Tiempo de resolver el problema:", finished_time - start_time)

    def parser_solution(self):
        if self.model.status == GRB.Status.OPTIMAL:
            clinic_cost = self.clinic_cost
            if (self.model.objVal + clinic_cost) <= HospitalNetwork.best_solution:
                HospitalNetwork.best_solution = self.model.objVal + clinic_cost
                with self.lock:
                    x = list()
                    y = list()
                    w = list()
                    z = list()
                    b = list()
                    tras = list()
                    for j, g, TLL, HLL, dead_line in self.jgthd:
                        for t in range(min(dead_line, t_max)):
                            for h in range(h_max):
                                for q in range(CQ[h]):
                                    if self.X[j, t, h, q].x:
                                        x.append(
                                            {
                                                "dia": t,
                                                "paciente": j,
                                                "GRD": g,
                                                "hospital": h,
                                                "quirofano": q,
                                            }
                                        )

                        if self.W[j].x:
                            w.append({"paciente": j})  # , 'GRD': g, 'dia': t})
                        for h2 in range(h_max):
                            if HLL != h2:
                                if self.T[j, HLL, h2].x:
                                    tras.append(
                                        {
                                            "paciente": j,
                                            "hospital1": HLL,
                                            "hospital2": h2,
                                        }
                                    )

                    for t in range(t_max):
                        for g in range(g_max):
                            for h in range(h_max):
                                for q in range(CQ[h]):
                                    if self.Y[g, t, h, q]:
                                        y.append(
                                            {
                                                "dia": t,
                                                "hospital": h,
                                                "quirofano": q,
                                                "GRD": g,
                                            }
                                        )
                        for m in range(m_max):
                            for h in range(h_max):
                                for q in range(CQ[h]):
                                    if self.Z[m, h, q, t].x:
                                        z.append(
                                            {
                                                "dia": t,
                                                "medicos": m,
                                                "valor": self.Z[m, h, q, t].x,
                                                "hospital": h,
                                                "quirofano": q,
                                            }
                                        )
                            for h1 in range(h_max):
                                for h2 in range(h_max):
                                    if h1 != h2:
                                        if self.B[h1, h2, m, t].x:
                                            b.append(
                                                {
                                                    "dia": t,
                                                    "medicos": m,
                                                    "valor": self.B[h1, h2, m, t].x,
                                                    "hospital 1": h1,
                                                    "hospital 2": h2,
                                                }
                                            )

                    x = sorted(x, key=lambda k: k["dia"])

                    data = {"X": x, "Y": y, "W": w, "Z": z, "B": b, "T": tras}

                    self.summary(**data)

                    with open(self.save_name + ".txt", "w") as file:
                        for dic, value in data.items():
                            file.write(f"\n{dic}\n")
                            file.write("\n".join([str(x) for x in value]) + "\n")

                    with open(self.save_name + ".json", "w") as fp:
                        json.dump(data, fp)
            else:
                print("No solution")

    def run(self):
        start_time = time.time()
        self.generate_vars()
        self.generate_restrictions()
        self.set_objetive()
        self.optimize_model()
        self.parser_solution()
        finished_time = time.time()
        print("Tiempo total de ejecucion:", finished_time - start_time)

    @property
    def clinic_cost(self):
        return sum(C[p.hospital] + CO[p.grd] for p in self.red.go_to_clinic)

    def summary(self, X, Y, W, Z, B, T):
        string = """\
        Resumen general
        N° de pacientes que llegaron al hospital:   {0}
        N° de pacientes analizados:                 {1}
        N° total de pacientes atendidos en clinica: {2}
        Costo Fase 1:                               {11}
        Costo Total:                                {3}

        Resumen de la optimizacion
        Costo Optimizacion:                 {4}
        N° de pacientes atendidos (X):      {5}
        N° de quirofanos asignados (Y):     {6}
        N° de pacientes en clinica (W):     {7}
        N° de grupos medicos formados (Z):  {8}
        N° de traslado de medicos (B):      {9}
        N° de traslado de pacientes (T):    {10}
        """.format(
            self.n_week,
            len(self.jgthd),
            len(W) + self.n_week,
            round(self.model.objVal + self.clinic_cost, 3),
            round(self.model.objVal),
            len(X),
            len(Y),
            len(W),
            len(Z) // (m_max + 1),
            len(B) // (m_max + 1),
            len(T),
            round(self.clinic_cost),
        )
        with open("Resumen_optimizacion.txt", "w") as file:
            file.write(string)
        print(string)
        # return string


if __name__ == "__main__":
    FOLDER = "Archivos/"
    # ARCHIVE_NAME = 'Datos.csv'
    ARCHIVE_NAME = "lista_pacientes.json"
    n = 1
    for _ in range(n):
        HN = HospitalNetwork(
            FOLDER + ARCHIVE_NAME, 3500, f"RESULTADOS/{n}_ITERACIONES", gap=0.3
        )
        HN.start()
