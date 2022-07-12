from parameters import *
from files import open_datos, open_json
from functools import reduce
from itertools import groupby
from random import shuffle, choice


def groupby_type(db, type1="ide"):
    return {k: list(v) for k, v in groupby(db, lambda x: getattr(x, type1))}


class Patience:
    def __init__(self, ide, grd, hospital, dead_line, arrival_time=0):
        self.ide = ide
        self.grd = grd
        self.arrival_time = arrival_time
        self.hospital = hospital
        self.dead_line = dead_line

    @staticmethod
    def medical_staff_relation(patience):
        """
        P-> Personal médico del tipo m necesario para operar GRD tipo g
        PD-># Personal médico disponible de la especialidad m en toda la red

        """
        suma = 0
        for i in range(m_max):
            suma += P[i, patience.grd] / PD[i]
        return suma

    @property
    def jgthd(self):
        return [self.ide, self.grd, self.arrival_time, self.hospital, self.dead_line]

    def __lt__(self, other):
        my_suma = 0
        other_suma = 0
        ponderation = {"time_cost": 0.5, "staff": 0.3, "dead_line": 0.2}
        dic = dict()
        dic["time_cost"] = (D[self.grd] / CO[self.grd], D[other.grd] / CO[other.grd])
        dic["staff"] = self.medical_staff_relation(self), self.medical_staff_relation(
            other
        )
        suma_dead_line = (
            self.dead_line + other.dead_line
            if self.dead_line + other.dead_line > 0
            else 1
        )
        dic["dead_line"] = (
            self.dead_line / suma_dead_line,
            other.dead_line / suma_dead_line,
        )
        for k, v in dic.items():
            my_suma += dic[k][0] * ponderation[k]
            other_suma += dic[k][1] * ponderation[k]
        return my_suma < other_suma

    def __repr__(self):
        return f"ide: {self.ide}, grd: {self.grd}, hospital: {self.hospital}, dead_line: {self.dead_line}"


class Red:
    def __init__(self, file_name):
        # patiences = [Patience(*data) for data in open_datos(file_name, n)]
        patiences = [Patience(**data) for data in open_json(file_name)]
        self.patiences = sorted(patiences)
        self.n_week = len(patiences)

    @property
    def average_hospital_time(self):
        total = 0
        acumulative = 0
        for h in range(h_max):
            acumulative += H[h] * CQ[h]
            total += CQ[h]
        return acumulative / total

    @property
    def selected_patiences(self):
        # average_operation_time = reduce(lambda x, y: x + D[y.grd], self.patiences, 0) / len(self.patiences)
        # x = 1250
        x = 1230
        average_operation_time = (
            reduce(lambda x, y: x + D[y.grd], self.patiences[:x], 0) / x
        )
        n = int(self.average_hospital_time * h_max * average_operation_time * t_max) + 1
        self.go_to_clinic = self.patiences[max(x, n) :]
        return self.patiences[: max(x, n)]

    @property
    def selected_patiences_jgthd(self):
        return [patience.jgthd for patience in self.selected_patiences]

    @property
    def ponderation_of_quirofanos(self):
        data_base = groupby_type(self.selected_patiences, "grd")
        new_dict = dict()
        for grd, lista in data_base.items():
            new_dict[grd] = len(lista)
        return new_dict

    def sum_grd(self, Y, t, h, q):
        suma = 0
        for g in range(g_max):
            if Y[g, t, h, q]:
                suma += 0
        return suma

    def restar_personal_medico(self, pd, grd):
        new_dic = pd.copy()
        for m in range(m_max):
            if pd[m] - P[m, grd] <= 0:
                return False
            new_dic[grd] = pd[grd] - P[m, grd]
        return new_dic

    def quirofano_repartition(self):
        """
        Utilizando solo un grd por dia
        """
        ponderation_of_quirofanos = self.ponderation_of_quirofanos
        Y = {
            (g, t, h, q): 0
            for g in range(g_max)
            for t in range(t_max)
            for h in range(h_max)
            for q in range(CQ[h])
        }
        revisados = []
        pd = PD.copy()
        for day in range(t_max):
            all_quirofanos = [(h, q) for h in range(h_max) for q in range(CQ[h])]
            shuffle(all_quirofanos)
            for tupla in all_quirofanos:
                if ponderation_of_quirofanos:
                    while True:
                        grd, n = choice(list(ponderation_of_quirofanos.items()))
                        if (day, *tupla) not in revisados:
                            revisados.append((day, *tupla))
                            break
                            # if self.sum_grd(Y, day, *tupla) <=1:
                            # break
                    pd = self.restar_personal_medico(pd, grd)
                    if not pd:
                        return Y
                    if n > 0:
                        Y[(grd, day, *tupla)] = 1
                        ponderation_of_quirofanos[grd] = n - 1
                    if n == 1:
                        del ponderation_of_quirofanos[grd]
                else:
                    print("WARNING: FALTAN QUIROFANOS")
                    return Y
        return Y  # Y[g, t, h, q]


if __name__ == "__main__":
    r = Red("Archivos/" + "Datos.csv", 3500)
    for p in r.selected_patiences:
        # print(p)
        pass
    print(len(r.selected_patiences))
    print(len(r.go_to_clinict))
    n = 0
    for k, v in r.quirofano_repartition().items():
        if v:
            print(k)
            n += 1
    print(n)
