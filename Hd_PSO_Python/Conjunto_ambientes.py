#-*- coding: utf-8 -*-
import numpy as np
import scipy.spatial.distance as sp
import copy
from PSO import PSO

import scipy.spatial.distance as dist

class Ambiente():
    def __init__(self, picos, Gpico):
        self.picos = picos
        self.Gpico = Gpico

class Conjunto_ambientes():
    def __init__(self, M):
        self.M = M
        self.vetor_ambientes = []
        self.rj = 0.5
        self.qtd_memoria = 0
        self.tamanho_max_memoria = 10
        self.X_old_point = []
        self.X_test_fitness = 0   
        
    def Distancia_vetores(self, a, b):
        resultado = sp.norm(a-b)
        return resultado
    
    def MIN(self, a, B):
        distancia = []
        for i in B:
            distancia.append(self.Distancia_vetores(a, i.dimensao))
        j = np.argmin(distancia) 
        resultado = distancia[j]   
        return resultado
    
    def Distancia_ambientes(self, A, B):
        distancia = []
        for i in A: 
            distancia.append(self.MIN(i.dimensao, B))
        j = np.argmin(distancia)
        resultado = (1/len(A))*distancia[j]
        return resultado
    
    def Relembrar_ambiente(self, A):
        
        distancias = []
        j = 0
        
        if(self.qtd_memoria != 0):
            for B in self.vetor_ambientes:
                c = self.Distancia_ambientes(A.picos, B.picos)
                distancias.append(c)
            
            j = np.argmin(distancias)
            if(distancias[j] <= self.M):
                for p in A.picos:
                    for i in range(len(A.picos[0].dimensao)):
                        p.dimensao[i] = p.dimensao[i] + self.rj*(self.vetor_ambientes[j].Gpico.dimensao[i] - p.dimensao[i])
                
                for i in range(len(A.picos[0].dimensao)):
                        A.Gpico.dimensao[i] = A.Gpico.dimensao[i] + self.rj*(self.vetor_ambientes[j].Gpico.dimensao[i] - A.Gpico.dimensao[i])
                        
            print("\n-> Ambiente Semelhante! Distancia do ambiente: ", distancias[j])

            return A
        
    def Adicionar_ambiente(self, ambiente):
        if(self.qtd_memoria < self.tamanho_max_memoria):
            self.vetor_ambientes.append(ambiente)
            self.qtd_memoria +=1
        else:
            del self.vetor_ambientes[0]
            self.vetor_ambientes.append(ambiente)
           
#a = array([1,2,7,9,0])
#b = array([66,7,7,8,99])
#B = array([b,[7,1,2,1,2],[6,12,4,1,22]])
#A = array([[10,9,8,7,6],[1,2,3,4,5],[6,17,8,9,10]])

#calc = Conjunto_ambientes(3)
#c = calc.Distancia_vetores(a, b)
#print(c)
#d = calc.MIN(a, B)
#print(d)
#e = calc.Distancia_ambientes(A, B)
#print(e)
#f = calc.Relembrar_ambiente(A, B)