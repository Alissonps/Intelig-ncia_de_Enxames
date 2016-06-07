#-*- coding: utf-8 -*-
from PSO import PSO
from Conjunto_ambientes import Ambiente, Conjunto_ambientes
import copy
import numpy as np
import scipy.spatial.distance as sp
#TesteBranch

contador = 0
contador2 = 0
mudanca_Aconteceu = False

ambiente = 0
direcao = "direita"
pl = 5
media_anterior = 0
current_particle = []
r_conv = 1
m = 5

class Algoritmo():
    def __init__(self):
        self.X_old_point = []
        self.X_old_fitness = 1000
        self.finder = []
        self.tracker = []
        self.conj_ambientes = []
        self.ambiente_atual = []
        self.MCP = []
        self.execucoes = 30
        self.best_solution = []
        self.track_fitness = 0
        self.congelar = False
        
    def Media(self, particulas):
        media = 0
        for i in particulas:
            media += copy.deepcopy(i.fitness)
        media = media/len(particulas)
        return media    
        
    def Inicializar(self):
        self.finder = PSO(1000, 10, 1, 2, 2, 1000)
        self.finder.PreencherMCP(0)
        
        self.ambiente_atual = Ambiente(self.finder.particulas, self.finder.gbest)
        
        self.conj_ambientes = Conjunto_ambientes(1)
        self.conj_ambientes.Adicionar_ambiente(self.ambiente_atual)
        
        self.tracker = PSO(1000, 10, 1, 2, 2, 1000, self.finder.old_tree)
        self.tracker.particulas = copy.deepcopy(self.finder.particulas)
        self.tracker.gbest = copy.deepcopy(self.finder.gbest)
        
        self.best_solution = copy.deepcopy(self.tracker.gbest)
        
        self.MCP = self.finder.old_tree
        
        self.X_old_point = self.finder.gbest.dimensao
        self.X_old_fitness = self.finder.gbest.fitness
    
    def Relembrar_Ambiente(self, Ambiente_Atual):
        self.ambiente_atual = copy.deepcopy(self.conj_ambientes.Relembrar_ambiente(Ambiente_Atual))
        self.finder.particulas = copy.deepcopy(self.ambiente_atual.picos)
        self.finder.gbest = copy.deepcopy(self.ambiente_atual.Gpico)
    
    def Detectar_mudanca(self, execucao, mean_after):
        global contador2
        
        media = self.Media(self.finder.particulas)
        
        if(media > mean_after):
            contador2 += 1
            
            if(contador2 > 3):
            
                X_new_point =  self.finder.gbest.dimensao
                X_new_fitness = self.finder.gbest.fitness
                               
                if(self.X_old_fitness != X_new_fitness):
                    print("\n-> MUDANCA ACONTECEU!!!!!")
                    #salva o ambiente antigo                
                    ambiente = Ambiente(self.tracker.particulas, self.tracker.gbest)
                    self.conj_ambientes.Adicionar_ambiente(ambiente)
                    #reinicia o enxame finder
                    self.finder = PSO(1000, 10, 1, 2, 2, 1000)
                    self.finder.PreencherMCP(execucao)
                    #reinicia o enxame tracker com as particulas do enxame finder                        
                    self.tracker = PSO(1000, 10, 1, 2, 2, 1000, self.finder.old_tree)
                    self.tracker.particulas = copy.deepcopy(self.finder.particulas)
                    self.tracker.gbest = copy.deepcopy(self.finder.gbest)
                    #salva a memoria de curto prazo
                    self.MCP = copy.deepcopy(self.finder.old_tree)
                    #salva a solucao teste                
                    self.X_old_point = copy.deepcopy(X_new_point)
                    self.X_old_fitness = copy.deepcopy(X_new_fitness)
                    #descongelar o enxame
                    self.congelar = False 
                    global contador, contador2, mudanca_Aconteceu
                    mudanca_Aconteceu = True
                    contador = 0
                    contador2 = 0
                    #atualizar melhor solução do ambiente
                    self.best_solution = copy.deepcopy(self.tracker.gbest)
        
        else:
            contador2 += 0
        
        global media_anterior
        
        media_anterior = media
        
    def Swarm_Finder(self, execucao):
        global mudanca_Aconteceu
        
        if(mudanca_Aconteceu == True):
            self.finder.old_tree = self.MCP
            self.finder.Executar_2(execucao)
            mudanca_Aconteceu = False
        else:
            self.finder.old_tree = self.MCP
            self.finder.Executar_2(execucao)
    
    def Swarm_Tracker(self, execucao):
        global contador

        self.tracker.Refinamento(execucao)
        
        fitness_atual = self.tracker.gbest.fitness
        
        if(execucao == 0):
            self.track_fitness = fitness_atual
            
    def Exclusion(self, swarm):
        r_excel = 0.5
        
        for i in swarm.particulas:
            if((sp.norm(i.dimensao-swarm.gbest.dimensao)) < r_excel):
               swarm = PSO(1000, 10, 1, 2, 2, 1000)
               swarm.Criar_Particula()
    
        return swarm
    
    def Pendulum(self):
        global direcao, ambiente
        
        if(direcao == "direita"):
            if(ambiente < pl):
                ambiente = ambiente + 1
            elif(ambiente == pl):
                direcao = "esquerda"
                ambiente = ambiente - 1
        elif(direcao == "esquerda"):
            if(ambiente > 1):
                ambiente = ambiente - 1
            elif(ambiente == 1):
                direcao = "direita"
                ambiente = ambiente + 1
        return ambiente
            
    def Executar(self):
        
        self.Inicializar()
        
        global media_anterior
        valores = []
        suporte = []
        solucao_geral = []
        
        
        for i in range(self.execucoes):
            
            print("\n----------------------------  Execução: ", i , "------------------------------------------------------")
            

            ambiente = self.Pendulum()
            
            self.Relembrar_Ambiente(self.ambiente_atual)
            
            self.Detectar_mudanca(ambiente, media_anterior)
                          
            if((self.congelar == False)):     
                self.Swarm_Finder(ambiente)
                print("-> Finder: ", self.finder.gbest.fitness)
                
                self.Exclusion(self.finder)
                
                suporte.append(self.finder.gbest.fitness)
                global current_particle 
                current_particle.append(self.finder.gbest)
            
                #finderConvergenceChecking
                if(i >= 4):
                    if(((suporte[i-3] - self.finder.gbest.fitness) < r_conv) or (sp.norm(current_particle[i-3].dimensao-self.finder.gbest.dimensao) < (r_conv/5))):
                        self.tracker.particulas = copy.deepcopy(self.finder.particulas)
                        self.tracker.gbest = copy.deepcopy(self.finder.gbest)
                        

            self.Swarm_Tracker(ambiente)
            print("-> Tracker: ", self.tracker.gbest.fitness)
                            
            print("-> Melhor solução: ", self.tracker.gbest.fitness)     
            solucao_geral.append(self.tracker.gbest.fitness)
            
            
            valores.append(self.finder.gbest.fitness)
                    
            #Swarm_freezing
            if(i >= 4):
                if(((valores[i-2] - self.finder.gbest.fitness) < r_conv) or (sp.norm(current_particle[i-2].dimensao-self.finder.gbest.dimensao) < (r_conv/5))):
                    self.congelar = True
          
        print("\nMedia:" , np.mean(solucao_geral))
        print("Desvio:" , np.std(solucao_geral))  
              
    
        
alg = Algoritmo()
alg.Executar()                    
                    