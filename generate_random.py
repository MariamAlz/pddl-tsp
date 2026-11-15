import random
import math

def randomly_generate(num_cities):
    #count = 5
    #file_name = "pb{}.pddl".format(count)
    file_name = "problems/pb{}.pddl".format(num_cities)
    with open(file_name, 'w') as f:
        f.write("(define (problem pb{})\n".format(num_cities))
        f.write("  (:domain tsp)\n")
        #num_cities = 20000
        objects = ""
        all_cities = set()
        for i in range(1, num_cities+1): 
            objects = objects + "c" + str(i) + " "
            all_cities.add("c"+str(i))
        f.write("  (:objects {}- position)\n".format(objects))
        f.write("  (:init\n")
        f.write("    ; Directed graph\n")
        connections = []
        num_combinations = math.factorial(num_cities)/(math.factorial(2) * math.factorial(num_cities-2))
        max = int(num_combinations/2)
        num_connections = 0
        while all_cities != set() and num_connections <= max:
            #for i in range(num_cities, max): 
                city1 = "c"+str(random.randint(1,num_cities))
                city2 = "c"+str(random.randint(1,num_cities))
                while((city2 == city1) or ((city1, city2) in list(set(connections)))):
                    city2 = "c"+str(random.randint(1,num_cities))
                f.write("    (connected {} {})\n".format(city1, city2))
                f.write("    (connected {} {})\n".format(city2, city1))
                num_connections = num_connections + 1
                connections.append((city1, city2))
                connections.append((city2, city1))
                if (city1 in all_cities):
                    all_cities.remove(city1)
                if (city2 in all_cities):
                    all_cities.remove(city2)
        f.write("    ; Start\n")
        at = "c"+str(random.randint(1,num_cities))
        f.write("    (at {})\n".format(at))
        f.write("  )\n")
        f.write("\n")
        f.write("  (:goal (and\n")
        f.write("    (at {})\n".format(at))
        for i in range(1, num_cities+1): 
            f.write("    (visited {})\n".format("c"+str(i)))
        f.write("  ))\n")
        f.write(")")

if __name__ == '__main__':
    for i in range(1000, 20000+1000, 1000):
        #randomly_generate(i)
        print(i)