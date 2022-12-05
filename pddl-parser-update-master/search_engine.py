from pddl_parser.PDDL import *

from search import *

from time import perf_counter
import numpy as np
import matplotlib.pyplot as plt

def apply_search2(func, name, index):
    start_time = time.perf_counter_ns()
    solution, history, maximal = func
    end_time = time.perf_counter_ns() - start_time
    return end_time, history, solution, maximal

def apply_search(func, name):
    start_time = time.perf_counter_ns()
    solution, history, maximal = func
    end_time = time.perf_counter_ns() - start_time
    historyLength[state].append(len(history))
    solutionLength[state].append(len(solution.getPath()))
    maxFrontierLength[state].append(maximal)
    print(name)
    print (name, [(node.state, node.action) for node in solution.getPath()])
    print ("Exploration History:", [node.state for node in history])
    return end_time


# -----------------------------------------------
# Main
# -----------------------------------------------

if __name__ == '__main__':

    import sys, pprint, time, argparse
    import pandas as pd
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser()
    parser.add_argument('-domain', type = str, default = "domain.pddl", 
					help = "Domain file")
    parser.add_argument('-problem', type = str, default = "problem.pddl", 
					help = "Problem file")
    parser.add_argument('-search', default = "bfs",
					help = "Search functions")
    arg = parser.parse_args()

    #domain = './examples/tsp/tsp.pddl'
    #problem = './examples/tsp/pb1.pddl'
    
    parser = PDDL_Parser()
    parser.parse_domain(arg.domain)
    parser.parse_problem(arg.problem)
    '''
    print('----------------------------')
    pprint.pprint(parser.scan_tokens(domain))
    print('----------------------------')
    pprint.pprint(parser.scan_tokens(problem))
    print('----------------------------')
    parser.parse_domain(domain)
    parser.parse_problem(problem)
    print('Domain name: ' + parser.domain_name)
    for act in parser.actions:
        print(act)
    print('----------------------------')
    print('Problem name: ' + parser.problem_name)
    print('Objects: ' + str(parser.objects))
    print('State: ' + str([list(i) for i in parser.state]))
    print('Positive goals: ' + str([list(i) for i in parser.positive_goals]))
    print('Negative goals: ' + str([list(i) for i in parser.negative_goals]))
'''
    #Plotting
    '''
    labels = []
    intlabels = []
    timeLength={}
    historyLength={}
    solutionLength={}
    maxFrontierLength={}
    for i in range(1000, 5000+1000, 1000):
        intlabels.append(i)

    for l in intlabels:
        timeLength[l]=[]
        historyLength[l]=[]
        solutionLength[l]=[]
        maxFrontierLength[l]=[]

    for i in range(1000, 5000+1000, 1000):
        parser.parse_problem("pb{}.pddl".format(i))
        labels.append(str(i))

        h = create_heuristics(parser.objects)
        all_connections = create_connections(parser.state)
        connections = create_unique(all_connections)
        locations = create_locations(parser.objects, connections)
        rg = reverse_goal_state(parser.positive_goals)
        init_city = find_at_city(parser.state)

        state = rg[len(rg)-1]

        #for state in allStates:
        #historyLength[state]=[]
        #solutionLength[state]=[]
        #maxFrontierLength[state]=[]

        salesman = NavigationProblem(init_city, state, connections)

        print("{}: ".format(i))
        bfs_time, bfs_h, bfs_s, bfs_m = apply_search2(breadth_first_graph_search(salesman), "Breadth First Search", i)
        print("Breadth First Search time: {}\n".format(bfs_time))
        timeLength[i].append(bfs_time)
        historyLength[i].append(len(bfs_h))
        solutionLength[i].append(len(bfs_s.getPath()))
        maxFrontierLength[i].append(bfs_m)
        dfs_time, dfs_h, dfs_s, dfs_m = apply_search2(depth_first_graph_search(NavigationProblem(init_city, state, connections)), "Depth First Search", i)
        print("Depth First Search time: {}\n".format(dfs_time))
        timeLength[i].append(dfs_time)
        historyLength[i].append(len(dfs_h))
        solutionLength[i].append(len(dfs_s.getPath()))
        maxFrontierLength[i].append(dfs_m)
        ucs_time,ucs_h,ucs_s,ucs_m = apply_search2(graph_search(salesman, PriorityQueue(ucs)), "Uniform Cost Search", i)
        print("Uniform Cost Search time: {}\n".format(ucs_time))
        timeLength[i].append(ucs_time)
        historyLength[i].append(len(ucs_h))
        solutionLength[i].append(len(ucs_s.getPath()))
        maxFrontierLength[i].append(ucs_m)
        astar_time, astar_h, astar_s, astar_m = apply_search2(graph_search(salesman, PriorityQueue(lambda node: node.path_cost + h[node.state])), "A* Search", i)
        print("A* Search time: {}\n".format(astar_time))
        timeLength[i].append(astar_time)
        historyLength[i].append(len(astar_h))
        solutionLength[i].append(len(astar_s.getPath()))
        maxFrontierLength[i].append(astar_m)
        bfgs_time, bfgs_h, bfgs_s, bfgs_m = apply_search2(graph_search(salesman, PriorityQueue(lambda node: h[node.state])), "Best First Greedy Search", i)
        print("Best First Greedy Search time: {}\n".format(bfgs_time))
        timeLength[i].append(bfgs_time)
        historyLength[i].append(len(bfgs_h))
        solutionLength[i].append(len(bfgs_s.getPath()))
        maxFrontierLength[i].append(bfgs_m)
        ids_time, ids_h, ids_s, ids_m = apply_search2(iterative_deep_graph_search(salesman), "Iterative Deepning Search", i)
        print("Iterative Deepning Search time: {}\n".format(ids_time))
        timeLength[i].append(ids_time)
        historyLength[i].append(len(ids_h))
        solutionLength[i].append(len(ids_s.getPath()))
        maxFrontierLength[i].append(ids_m)
        print(timeLength[i])
    
    print(timeLength)
    df = pd.DataFrame.from_dict(timeLength, orient='index')
    print(timeLength)

    labs = ["Breadth First", "Depth First", "Uniform Cost", "A-star", "Best First", "Iterative Deepning"]

    df.plot(kind="bar")
    plt.legend(labs)
    plt.title("Time elapsed (for running each search algorithm) vs. number of cities")
    plt.show()

    df = pd.DataFrame.from_dict(historyLength, orient='index')

    df.plot(kind="bar")
    plt.legend(labs)
    plt.title("History length vs. Number of cities")
    plt.show()

    df = pd.DataFrame.from_dict(solutionLength, orient='index')

    df.plot(kind="bar")
    plt.legend(labs)
    plt.title("Solution length vs. Number of cities")
    plt.show()

    df = pd.DataFrame.from_dict(maxFrontierLength, orient='index')

    df.plot(kind="bar")
    plt.legend(labs)
    plt.title("Max frontier length vs. Number of cities")
    plt.show()
    '''

    h = create_heuristics(parser.objects)
    all_connections = create_connections(parser.state)
    connections = create_unique(all_connections)
    locations = create_locations(parser.objects, connections)
    rg = rg = reverse_goal_state(parser.positive_goals)
    init_city = find_at_city(parser.state)
    #print('h = {}'.format(h))
    #print('all connections = {}'.format(all_connections))
    #print('unique connections = {}'.format(connections))
    #print('locations = {}'.format(locations))
    #print('goal state (in reverse) = {}'.format(rg))
    #print('init city = {}'.format(init_city))
    #print("\n")

    allStates = list(locations.keys())
    historyLength={}
    solutionLength={}
    maxFrontierLength={}

    for state in allStates:
        historyLength[state]=[]
        solutionLength[state]=[]
        maxFrontierLength[state]=[]
        #h[state] = int(math.sqrt((locations[state][0]-locations[init_city][0])**2 + (locations[state][1]-locations[init_city][1])**2))

    
    #if (arg.search != ('bfs' or 'dfs' or 'ids' or 'ucs' or 'bfgs' or 'astar')):
    if (arg.search == 'all'):
        state = rg[len(rg)-1]
        salesman = NavigationProblem(init_city, state, connections)
        #plt.clf()
        #nx.draw(salesman.graph, with_labels = True)
        #plt.show()
        bfs_time = apply_search(breadth_first_graph_search(salesman), "Breadth First Search")
        print("Breadth First Search time: {}\n".format(bfs_time))
        dfs_time = apply_search(depth_first_graph_search(NavigationProblem(init_city, state, connections)), "Depth First Search")
        print("Depth First Search time: {}\n".format(dfs_time))
        ucs_time = apply_search(graph_search(salesman, PriorityQueue(ucs)), "Uniform Cost Search")
        print("Uniform Cost Search time: {}\n".format(ucs_time))
        astar_time = apply_search(graph_search(salesman, PriorityQueue(lambda node: node.path_cost + h[node.state])), "A* Search")
        print("A* Search time: {}\n".format(astar_time))
        bfgs_time = apply_search(graph_search(salesman, PriorityQueue(lambda node: h[node.state])), "Best First Greedy Search")
        print("Best First Greedy Search time: {}\n".format(bfgs_time))
        ids_time = apply_search(iterative_deep_graph_search(salesman), "Iterative Deepning Search")
        print("Iterative Deepning Search time: {}\n".format(ids_time)) 
        '''
        labels = ["Breadth First", "Depth First", "Uniform Cost", "A-star", "Best First", "Iterative Deepning"]
        
        df = pd.DataFrame(solutionLength).T
        df.plot(kind="bar")
        plt.legend(labels)
        plt.title("Solution Length")
        plt.show()

        df = pd.DataFrame(historyLength).T
        df.plot(kind="bar")
        plt.legend(labels)
        plt.title("Exploration History Size")
        plt.show()

        df = pd.DataFrame(maxFrontierLength).T
        df.plot(kind="bar")
        plt.legend(labels)
        plt.title("Maximal Frontier Sizes")
        plt.show()
        '''
 
        # creating the dataset
        data = {'bfs':bfs_time, 'dfs':dfs_time, 'ucs':ucs_time, 'astar':astar_time, 'bfgs':bfgs_time, 'ids':ids_time}
        algorithms = list(data.keys())
        time_values = list(data.values())
  
        fig = plt.figure(figsize = (10, 5))
 
        # creating the bar plot
        plt.bar(algorithms, time_values, color ='maroon', width = 0.4)
 
        plt.xlabel("Algorithms used")
        plt.ylabel("Time elapsed")
        plt.title("Search Algorithms vs Time")
        plt.show()
    
    elif (arg.search == 'bfs'):
        start_time = time.time()
        state = rg[len(rg)-1]
        salesman=NavigationProblem(init_city, state, connections)
        print("from {} to {}:".format(init_city, state))
        apply_search(breadth_first_graph_search(salesman), "Breadth First Search")
        print('Time: ' + str(time.time() - start_time) + 's')
        #plt.clf()
        #nx.draw(salesman.graph, with_labels = True)
        #plt.show()

    elif (arg.search == 'dfs'):
        start_time = time.time()
        state = rg[len(rg)-1]
        salesman=NavigationProblem(init_city, state, connections)
        print("from {} to {}:".format(init_city, state))
        apply_search(depth_first_graph_search(salesman), "Depth First Search")
        print('Time: ' + str(time.time() - start_time) + 's')
        #plt.clf()
        #nx.draw(salesman.graph, with_labels = True)
        #plt.show()

    elif (arg.search == 'ucs'):
        start_time = time.time()
        state = rg[len(rg)-1]
        salesman=NavigationProblem(init_city, state, connections)
        print("from {} to {}:".format(init_city, state))
        apply_search(graph_search(salesman, PriorityQueue(ucs)), "Uniform Cost Search")
        print('Time: ' + str(time.time() - start_time) + 's')
        #plt.clf()
        #nx.draw(salesman.graph, with_labels = True)
        #plt.show()

    elif (arg.search == 'astar'):
        start_time = time.time()
        state = rg[len(rg)-1]
        salesman=NavigationProblem(init_city, state, connections)
        print("from {} to {}:".format(init_city, state))
        apply_search(graph_search(salesman, PriorityQueue(lambda node: node.path_cost + h[node.state])), "A* Search")
        print('Time: ' + str(time.time() - start_time) + 's')
        #plt.clf()
        #nx.draw(salesman.graph, with_labels = True)
        #plt.show()

    elif (arg.search == 'bfgs'):
        start_time = time.time()
        state = rg[len(rg)-1]
        salesman=NavigationProblem(init_city, state, connections)
        print("from {} to {}:".format(init_city, state))
        apply_search(graph_search(salesman, PriorityQueue(lambda node: h[node.state])), "Best First Greedy Search")
        print('Time: ' + str(time.time() - start_time) + 's')
        #plt.clf()
        #nx.draw(salesman.graph, with_labels = True)
        #plt.show()

    elif (arg.search == 'ids'):
        start_time = time.time()
        state = rg[len(rg)-1]
        salesman=NavigationProblem(init_city, state, connections)
        print("from {} to {}:".format(init_city, state))
        apply_search(iterative_deep_graph_search(salesman), "Iterative Deepning Search")
        print('Time: ' + str(time.time() - start_time) + 's')
        #plt.clf()
        #nx.draw(salesman.graph, with_labels = True)
        #plt.show()
    
    else:
        print("Incorrect options. Please try from the list of options: [bfs|dfs|ids|ucs|bfgs|astar]")