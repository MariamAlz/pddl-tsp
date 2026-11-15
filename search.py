import networkx as nx
import numpy as np
import bisect
import random
import sys
import math
import matplotlib.pyplot as plt

class NavigationProblem:
    def __init__(self, initial, goal, connections, locations=None, directed=False):
        self.initial = initial
        self.goal = goal
        self.locations = locations
        self.graph = nx.DiGraph() if directed else nx.Graph()
        for cityA, cityB, distance in connections:
            self.graph.add_edge(cityA, cityB, cost=distance)            
    def successors(self, state):
        ## Exactly as defined in Lecture slides, 
        return [("go to %s" % city, connection['cost'], city) for city, connection in self.graph[state].items()]
    def goal_test(self, state):
        return state == self.goal

class Node:
    def __init__(self, state=None, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost        
    def getPath(self):
        """getting the path of parents up to the root"""
        currentNode = self
        path = [self]
        while currentNode.parent: ## stops when parent is None, ie root
            path.append(currentNode.parent)
            currentNode = currentNode.parent
        path.reverse() #from root to this node
        return path
    def expand(self, problem):
        successors = problem.successors(self.state)
        return [Node(newState, self, action, self.path_cost+cost) for (action, cost, newState) in successors]
    def __gt__(self, other): ## needed for tie breaks in priority queues
        return True
    def __repr__(self):
        return (self.state, self.action, self.path_cost)
    
class FIFO:
    def __init__(self):
        self.list = []
    def push(self, item):
        self.list.insert(0, item)  
    def pop(self):
        return self.list.pop()
class LIFO:
    def __init__(self):
        self.list = []
    def push(self, item):
        self.list.append(item)
    def pop(self):
        return self.list.pop()
class PriorityQueue:
    def __init__(self, f):
        self.list = []
        self.f = f
    def push(self, item):
        priority = self.f(item)
        bisect.insort(self.list, (priority, random.random(), item))
    def pop(self):
        return self.list.pop(0)[-1]
        
def graph_search(problem,frontier,depth=sys.maxsize):
    """Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    If two paths reach a state, only use the best one. [Fig. 3.18]"""
    explored = set()
    p = Node(problem.initial)
    p.depth = 0
    frontier.push(p)
    maxFrontierLength=1
    explorationHistory = []
    #goal_cities = ['albany', 'boston', 'pittsburgh', 'newyork', 'toronto']
    #goal_cities = set(goal_cities)
    while frontier:
        if not frontier.list:
            return None,None,None
        node = frontier.pop()
        explorationHistory.append(node)
        if problem.goal_test(node.state): 
            return node, explorationHistory, maxFrontierLength
        if node.state not in explored:
            #goal_cities.remove(node.state)
            explored.add(node.state)
            successors = node.expand(problem)
            if len(frontier.list) > maxFrontierLength:
                maxFrontierLength = len(frontier.list)
            for snode in successors:
                snode.depth = snode.parent.depth + 1
                if snode.depth<=depth:
                    frontier.push(snode)

def breadth_first_graph_search(problem):
    return graph_search(problem, FIFO())

def depth_first_graph_search(problem, depth= sys.maxsize):
    return graph_search(problem, LIFO(),depth)

def astar_graph_search(problem, f):
    return graph_search(problem, PriorityQueue(f))

def uniform_graph_search(problem, ucs):
    return graph_search(problem, PriorityQueue(ucs))

def depth_limited_search(problem, depth):
    return depth_first_graph_search(problem,depth=depth)

def iterative_deep_graph_search(problem, depth= sys.maxsize):
    loop = 0 
    depth = True   
    while depth:
        x,y,z = depth_limited_search(problem,loop)
        if x==None or y==None or z==None:
            pass
        else:
            return x,y,z
        loop+=1

#%%
# priority functions for Priority Queues used in UCS and A*, resp., if you are unfamiliar with lambda calc.
def ucs(node):
    return node.path_cost

def f(node):
    return node.path_cost + h[node.state]

