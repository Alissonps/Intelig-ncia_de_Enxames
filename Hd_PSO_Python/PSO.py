#-*- coding: utf-8 -*-
import random
from numpy import array
import numpy as np
import copy
import matplotlib.pyplot as plt
from BSP_Tree import BSP
from deap.benchmarks import movingpeaks, rastrigin
from numpy.random.mtrand import uniform

Xmax = 2
Xmin = -Xmax
posMax = 100
posMin = -posMax
mi = 100
r_cloud = 0.5

class Particulas():
    pass

class PSO():
    def __init__(self, iteracoes, numero_particulas, inercia, c1, c2, mudanca, old_tree = None):
        self.iteracoes = iteracoes
        self.numero_particulas = numero_particulas
        self.numero_dimensoes = 5
        self.inercia = inercia
        self.c1_fixo = c1
        self.c2_fixo = c2
        self.mudanca = mudanca
        self.particulas = []
        self.gbest = []
        self.old_tree = old_tree  
        
    def Criar_Particula(self):
        for i in range(self.numero_particulas):
            p = Particulas()
            p.dimensao = array([random.random() for i in range(self.numero_dimensoes)])
            p.fitness = self.Funcao(p.dimensao, 0)
            p.velocidade = array([0.0 for i in range(self.numero_dimensoes)])
            p.best = p.dimensao
            p.fit_best = p.fitness
            p.c1 = self.c1_fixo
            p.c2 = self.c2_fixo
            p.inercia = self.inercia
            p.phi = 0
            self.particulas.append(p)
        
        self.gbest = self.particulas[0]
        
    def Funcao(self, dimensao, execucao):

        sc = movingpeaks.SCENARIO_2
        sc["npeaks"] = 30
        sc["period"] = 5000 #500, 1000, 2500, 5000, 10000
        sc["height_severity"] = 7 
        sc["width_severity"] = 1
        sc["move_severity"] = 1 #1,2,3,5
        sc["lambda_"] = 0
        sc["max_coord"] = 100
        sc["min_coord"] = 0
        sc["max_height"] = 70
        sc["min_height"] = 30
        sc["max_width"] = 12
        sc["min_width"] = 1
        
        rnd = random.Random()
        rnd.seed(execucao)
        mp = movingpeaks.MovingPeaks(dim=self.numero_dimensoes, random=rnd, **sc)       
        fitness = mp.__call__(dimensao)
        melhor = mp.globalMaximum()
        resultado = fitness[0]-melhor[0]
        return np.abs(resultado)
    
    def Fitness(self, execucao):
        
        if(self.old_tree.maturidade >= self.old_tree.limiar):   
            for i in self.particulas:
                i.fitness = self.old_tree.get_node(i.dimensao, self.old_tree.maturidade)
                if(i.fitness <= i.fit_best):
                    i.fitness = self.Funcao(i.dimensao, execucao)
               
        else:
            for i in self.particulas:   
                i.fitness = self.Funcao(i.dimensao, execucao)
    
    def Fitness2(self, execucao):
        for i in self.particulas:   
            i.fitness = self.Funcao(i.dimensao, execucao)
                             
    def Velocidade(self):
        calculo_c1 = 0
        calculo_c2 = 0
        
        for i in self.particulas:
            for j in range(len(i.dimensao)):
                calculo_c1 = (i.best[j] - i.dimensao[j])
                calculo_c2 = (self.gbest.dimensao[j] - i.dimensao[j])
                
                influecia_inercia = (self.inercia * i.velocidade[j])
                influencia_cognitiva = ((self.c1_fixo * random.random()) * calculo_c1)
                influecia_social = ((self.c2_fixo * random.random()) * calculo_c2)
              
                i.velocidade[j] = influecia_inercia + influencia_cognitiva + influecia_social
                
                if (i.velocidade[j] >= Xmax):
                    i.velocidade[j] = Xmax
                elif(i.velocidade[j] <= Xmin):
                    i.velocidade[j] = Xmin
              
    def Atualizar_particulas(self):
        for i in self.particulas:
            for j in range(len(i.dimensao)):
                i.dimensao[j] = i.dimensao[j] + i.velocidade[j]
                
                if (i.dimensao[j] >= posMax):
                    i.dimensao[j] = posMax
                elif(i.dimensao[j] <= posMin):
                    i.dimensao[j] = posMin
    
    def Atualizar_parametros(self, iteracao):
        for i in self.particulas:
            parte1 = 0
            parte2 = 0
            
            for j in range(len(i.dimensao)):
                parte1 = parte1 + self.gbest.dimensao[j] - i.dimensao[j]
                parte2 = parte2 + i.best[j] - i.dimensao[j]
                
                if(parte1 == 0):
                    parte1 = 1
                if(parte2 == 0):
                    parte2 = 1
                    
            i.phi = abs(parte1/parte2)
            
        for i in self.particulas:
            ln = np.log(i.phi)
            calculo = i.phi * (iteracao - ((1 + ln) * self.iteracoes) / mi)
            i.inercia = ((self.inercia_inicial - self.inercia_final) / (1 + np.exp(calculo))) + self.inercia_final
            i.c1 = self.c1_fixo * (i.phi ** (-1))
            i.c2 = self.c2_fixo * i.phi
       
    def Pbest(self, old_tree):
        for i in self.particulas:
            if(i.fit_best >= i.fitness):
                i.best = i.dimensao
                i.fit_best = i.fitness
                
                if(old_tree.maturidade <= old_tree.limiar):
                    new_tree = BSP(i.dimensao, i.fitness)
                    old_tree.add_node(new_tree)  

    def Gbest(self):
        for i in self.particulas:
            if(i.fitness <= self.gbest.fitness):
                self.gbest = copy.deepcopy(i)
    
    def Fine_Tuning(self, execucao):
        x_new = []
        p_x_new = 0
        global r_cloud
        rj = uniform(-1,1)
        w_max = 0.9
        w_min = 0.6
            
        for k in range(len(self.gbest.dimensao)):
            x_new.append(self.gbest.dimensao[k] + (r_cloud * rj))
            
        p_x_new = self.old_tree.get_node(x_new, self.old_tree.maturidade)
        p_g_best = self.old_tree.get_node(self.gbest.dimensao, self.old_tree.maturidade)
        
        if(p_x_new <= p_g_best):
            p_x_new = self.Funcao(x_new, execucao)
            if(p_x_new <= self.gbest.fitness):
                self.gbest.dimensao = copy.deepcopy(x_new)
                self.gbest.fitness = copy.deepcopy(p_x_new)
            
        r_cloud = r_cloud * (w_min + (random.random() * (w_max - w_min))) 

    def PreencherMCP(self, execucao):
        
        self.Criar_Particula()       
        
        if(self.old_tree == None):
            dimensao = self.particulas[0].dimensao
            fit = self.particulas[0].fitness
            old_tree = BSP(dimensao, fit)
            old_tree.porcentagem = 0.005
            self.old_tree = old_tree
            
        for i in range(self.iteracoes):
            
            self.Fitness2(execucao)
            self.Gbest()
            self.Pbest(self.old_tree)
            self.Velocidade()
            self.Atualizar_particulas()
            
            if(self.old_tree.maturidade >= 1):
                print("    -> Iteracao: %d" % (i) + " - Melhor Fitness ", self.gbest.fitness)
                print("    -> Maturidade da arvore: ", self.old_tree.maturidade)
                break
            
    def Refinamento(self, execucao):
        j = 0
        for i in range(self.iteracoes):
            
            self.Fitness2(execucao)
            self.Gbest()
            self.Pbest(self.old_tree)
            self.Velocidade()
            self.Atualizar_particulas()
            self.Fine_Tuning(execucao)
            
            if(i == 0):
                fitness = copy.deepcopy(self.gbest.fitness)
            
            if(fitness == self.gbest.fitness):
                j+=1
            else:
                fitness = copy.deepcopy(self.gbest.fitness)
                j=0
                      
            if(j == self.mudanca):
                #print("        -Iteracao: %d" % (i) + " - Melhor Fitness ", self.gbest.fitness)
                break

    def Executar_2(self, execucao):
        j = 0
        for i in range(self.iteracoes):
            
            self.Fitness2(execucao)
            self.Gbest()
            self.Pbest(self.old_tree)
            self.Velocidade()
            self.Atualizar_particulas()
            
            if(i == 0):
                fitness = copy.deepcopy(self.gbest.fitness)
            
            if(fitness == self.gbest.fitness):
                j+=1
            else:
                fitness = copy.deepcopy(self.gbest.fitness)
                j=0
                      
            if(j == self.mudanca):
                #print("        -Iteracao: %d" % (i) + " - Melhor Fitness ", self.gbest.fitness)
                break

    
#finder = PSO(1000, 15, 1, 2, 2, 500)
#finder.PreencherMCP(0)
#finder.Executar(0)
#print("-------------------------Preenchendo até 70%-----------------------------------------------")        
#pso = PSO(100000, 15, 1, 0.2, 2.4, 1.3, 1000)
#pso.PreencherMCP(0)
#print(pso.old_tree.maturidade)
#print("-------------------------Preenchendo até 100%-----------------------------------------------")
#pso2 = PSO(100000, 15, 1, 0.2, 2.4, 1.3, 150)
#pso2.old_tree = pso.old_tree
#pso2.Executar(0)
#print("Refinamento: ")
#pso2.Refinamento(0)

