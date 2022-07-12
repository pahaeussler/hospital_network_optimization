# Hospital Network

Optimization model of schedule of operation rooms to optimize costs in a public Hospital Network.

## Solution
There is an 2 fase optimization and a simulation of the arrival of patiences.

## Optimization problem
### Objective Function

Minimize: Sum(
- Medical staff specialists moving between hospitals
- Patiens moving between hospitals
- Cost of attend patient in a clinic insted of a hospital

)

### Indexes:
- t : simulation time in days {1,2,3,4,5}
- j : patient j
- h : hospital h
- q : operating room q
- g : Diagnosis Related Groups(GRD) type g {1,2,3,4,5,6,7,8,9,10}
- m : corresponds to the medical specialty type m
- c : clinic c of the private system (it is only one, only the sub-index was added to facilitate understanding)

### Parameters:
- H(l,j,h) : 1 if patient j is admitted to the system at hospital h
- T(l,j,h) : arrival time of patient j to hospital h
- Ƭ(j) : time limit in which patient j must be treated
- P(g,m) : medical personnel of type m needed to operate DRG type g
- H(h) : hours of operation of the hospital h
- D(g)​: duration of the GRD type operation g → stochastic parameter (uncertainty)
- T(pg1,g2) : preparation time of an operating room between a type g1 DRG operation to another type g2
- C(h,g,c) : cost of transporting a patient with DRG type g from hospital h to clinic c
- CM(h1,h2) : cost of transferring a specialist from hospital h1 to another h2
- CP(h1,h2) : cost of transferring a patient from hospital h1 to another h2
- CO(g,c) : cost of operating a DRG g in clinic c
- P(Dm) : available medical staff of specialty m throughout the network

### Variables:
- Y(t,h,q,g): if I assign GRD g to operating room q of hospital h on day t
- X(j,t,h,q) ​:​ ​1 if I assign patient j with GRD g to operating room q of hospital h on day t
- W(j,t,c) ​: 1 if I assign patient j with GRD g on day t to clinic c
- Z(m,t,h,q : How many medical personnel of type m do I assign to the operating room q of hospital h on day t
- T(j,h1,h2) ​: 1 if the patient is transferred from hospital h1 to hospital h2
- B(ht,1,h2,m) ​: Medical staff specialists m moving from hospital h1 to hospital h2 on day t


### Restrictions:

- Take care of the patient in his time limit
- Maximum of two GRD per operating room per day
- Medical personnel needed in the hospital
- Do not exceed available medical personnel
- Staff calibration
- Do not exceed the time available in the operating room
- Attend and use the operating room only if that DRG is being attended
- Patient transfer calibration


## How to run

Run one time the optimization

```python
python3 main.py
```

Run the simulation
```python
python3 simulacion_fifo.py
```


## Outputs:
Take a loooong time, but generate results:

- Summary of optimization: Resumen_optimizacion.txt
- Schedule of patiences: resultado_optimizacion.json
- Patien list: lista_pacientes.json

## Project date:
June 2018