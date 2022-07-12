from parameters import *
from files import open_json
from fase_1_optimizacion import Patience
# from functools import reduce
# from itertools import groupby
from random import shuffle, choice
from collections import deque

class Quirofano:
    def __init__(self, hospital):
        self.hospital = hospital
        self.maximas_horas = H[hospital]
        self.uso = 0

    def horas_de_uso(self, grd):
        if D[grd] + self.uso <= maximas_horas:
            self.uso += D[grd]
            return True
        else:
            return False

def restar_personal_medico(pd, grd):
        new_dic = pd.copy()
        for m in range(m_max):
            if pd[m] - P[m, grd] <= 0:
                return False
            new_dic[grd] = pd[grd] - P[m, grd]
        return new_dic


def repartition(waiting_list):
    all_quirofanos = { h : [Quirofano(h) for q in range(CQ[h])] for h in range(h_max)}
    pd = PD.copy()
    full_quirofanos = {h : [] for h in range(h_max)}
    using_quirofanos = {h : [] for h in range(h_max)}
    while waiting_list:
        actual = waiting_list.popleft()
        pd = restar_personal_medico(pd, actual.grd)
        if not pd:
            return
        if using_quirofanos[actual.hospital]:

        print(pd)
        print(actual.hospital)


if __name__ == '__main__':
    file_name = 'lista_pacientes.json'
    patiences = deque(Patience(**data) for data in open_json(file_name))
    repartition(patiences)