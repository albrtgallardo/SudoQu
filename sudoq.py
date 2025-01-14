import numpy as np
from qiskit.visualization import plot_histogram, array_to_latex, plot_state_city, plot_bloch_vector, plot_state_qsphere
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator, QasmSimulator
from qiskit.quantum_info import Statevector, DensityMatrix, Operator, partial_trace
from qiskit_func import *
import matplotlib.pyplot as plt
import itertools
import operator
import math
import time


def permutation(classicalB):
    aux = [0, 1, 2, 3]                             
    list_out = []
    for i in aux:
        if i not in classicalB:                         
            list_out.append(i)
    list_out_2 = list(itertools.permutations(list_out)) 
    return list_out_2


def qbit_to_binary(perm):
    perm_bin = []
    for item in list(perm):
        binary_num = ""
        for i in item:
            prm_b = format(i,"b")
            if len(prm_b)==1:                  
                prm_b = '0' + prm_b
            binary_num = binary_num + prm_b
        perm_bin.append(binary_num)
    return perm_bin


def oracle(qc, l_qbits, l_perm_bin):
    for item in l_perm_bin:
        cont = 0                                            
        for j in item:
            if j == '0':
                qc.x(l_qbits[cont])
            cont+=1
        qc.h(l_qbits[0])
        qc.mcx(l_qbits[1:len(l_qbits)],l_qbits[0])           
        qc.h(l_qbits[0])
        cont = 0
        for j in item:                                      
            if j == '0':
                qc.x(l_qbits[cont])
            cont+=1
    return qc      


def reflector(qc, l_qbits):
    qc.h(l_qbits) 
    qc.x(l_qbits)
    qc.h(l_qbits[0])
    qc.mcx(l_qbits[1:len(l_qbits)],l_qbits[0])
    qc.h(l_qbits[0])
    qc.x(l_qbits)
    qc.h(l_qbits)
    return qc


def grover(qc,l_qbits,l_bits):    
    if len(l_qbits) == 2:           
        n_rep = 1
    elif len(l_qbits) == 4:
        n_rep = 1
    else:
        n_rep = 2  
    perm = permutation(l_bits)      
    perm_bin = qbit_to_binary(perm) 
    for i in range(n_rep):          
        oracle(qc,l_qbits,perm_bin)
        reflector(qc,qc.qubits)
    return qc  


def real_computer(qc,r):

    if r > 1:
        print('Ojo cuidao con el rango, que te fundes los minutos de IBM.')
    else:
        
        ### Loggeo en IBM ###

        IBM = IBMRuntime()
        service = IBM.qiskit_log()


        ### Ordenador Menos Ocupado ###
        
        print('\nBuscando Ordenador Menos Ocupado...')
        backend = service.least_busy(operational=True,simulator=False)
        qc = transpile(qc, backend)
        print('\nEjecutando el código en',backend,'...')

        ### Correr el Circuito ###

        sampler = Sampler(backend)
        job = sampler.run([qc])
        result = job.result()


        ### Medir Resultados ###

        counts = result[0].data.c0.get_counts()
        brisbane_dict=dict(sorted(counts.items(), key=operator.itemgetter(1))[-20:])
        plot_histogram(brisbane_dict)
        plt.show()

        pass


if __name__ == '__main__':

    nQbits = 14;                        
    q = QuantumRegister(nQbits)   
    c = ClassicalRegister(nQbits) 
    qc = QuantumCircuit(q,c)
    qc.h(range(nQbits))
    
    ### Ejecución del Algoritmo ###
    
    r = 4

    start_time = time.time()
    for _ in range(r):

        # Condiciones filas

        grover(qc,[q[0],q[1]],[0,1,2])
        grover(qc,[q[2],q[3],q[4],q[5]],[2,3])
        grover(qc,[q[6],q[7],q[8],q[9]],[2,3])
        grover(qc,[q[10],q[11],q[12],q[13]],[1,3])

        # Condiciones columnas

        grover(qc,[q[0],q[1],q[6],q[7]],[1,2])
        grover(qc,[q[2],q[3],q[10],q[11]],[0,3])
        grover(qc,[q[4],q[5],q[8],q[9]],[2,3])
        grover(qc,[q[12],q[13]],[1,2,3])

        # Condiciones bloques

        grover(qc,[q[0],q[1],q[2],q[3]],[0,2])
        grover(qc,[q[4],q[5]],[1,2,3])
        grover(qc,[q[6],q[7],q[10],q[11]],[1,3])
        grover(qc,[q[8],q[9],q[12],q[13]],[2,3])

    elapsed_time_grover = time.time() - start_time
    print(elapsed_time_grover,'s\n')

    
    ### Medición de Resultados ###

    qc.measure(q,c)
    simulator = AerSimulator()
    qc = transpile(qc, simulator)
    result = simulator.run(qc, shots=2048*128).result()
    counts = result.get_counts(qc)
    graph_dict=dict(sorted(counts.items(), key=operator.itemgetter(1))[-5:])
    max_state = max(graph_dict, key=graph_dict.get)
    print('|',max_state,'> :', graph_dict[max_state], f'shots ({graph_dict[max_state]/(2049*128)*100:.4f}%)')
    plot_histogram(graph_dict)
    plt.show()
    

    ### Mostrar Circuito ###

    qc.draw('mpl')
    plt.show()
    

    ### Ordenador Real ###

    while True:
        real = input('\nSimulación Real? (0: No, 1: Sí): ')

        if real == '0':
            break
        elif real == '1':
            real_computer(qc,r)
            break
        else:
            print('\nNo es una opción válida.\n')
