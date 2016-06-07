#-*- coding: utf-8 -*-
from random import random
import numpy as np
from numpy import array

class BSP(object):
    def __init__(self, key, value=None, left=None, right=None):
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        
        
        self.limiar = 1
        self.maturidade = 0
        self.porcentagem = 0.1
 
    def add_node(self, node):
        
        j = self.Max_indice(node.key, self.key)
        
        if (node.key[j] < self.key[j]):
            if self.left is None:
                self.left = node
            else:
                self.left.add_node(node)
        else:
            if self.right is None:
                self.right = node    
            else:
                self.right.add_node(node)
                
        self.Aumentar_porcentagem()
        
    def get_node(self, key, maturidade):
        
        if(maturidade >= self.limiar):
            
            j = self.Max_indice(key, self.key)
            
            if (key[j] < self.key[j]):
                if self.left != None:
                    return self.left.get_node(key, maturidade)
                else:
                    return self.value
            else:
                if self.right != None:
                    return self.right.get_node(key, maturidade)
                else:
                    return self.value
                
        else:
            return None
    
    def Aumentar_porcentagem(self):
        if(self.maturidade < self.limiar):
            self.maturidade += self.porcentagem
    
    def Max_indice(self, vetor1, vetor2):
        c = np.subtract(vetor1,vetor2)
        c = abs(c)
        j = np.argmax(c)
        return j
                               
#key = array([random() for i in range(4)]) 
#print(key)   
#old_tree = BSP(key)
#old_tree.value = np.sum(key)


#for i in range(0,10):
#    key = array([random() for i in range(4)])
#    fitness = np.sum(key)
#    new_tree = BSP(key, fitness)
#    old_tree.add_node(new_tree)
#    print("Nó: ", i , " Key: ", key, " fitness: " , fitness, "   maturidade: ", old_tree.maturidade)

#key = array([random() for i in range(4)])
#print(old_tree.get_node(key, old_tree.maturidade))

