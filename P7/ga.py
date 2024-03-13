import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import shutil
import time
import math

class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    # Update this individual's estimate of its fitness.
    # This can be expensive so we do it once and then cache the result.
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Print out the possible measurements or look at the implementation of metrics.py for other keys:
        # print(measurements.keys())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Modify this, and possibly add more metrics.  You can replace this with whatever code you like.
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients))
        return self

    # Return the cached fitness value or calculate it as needed.
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    # Mutate a genome into a new genome.  Note that this is a _genome_, not an individual!
    def mutate(self, genome):
        # STUDENT implement a mutation operator, also consider not mutating this individual
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc

        left = 1
        right = width - 1
        new_genome = copy.deepcopy(self.genome)
        for y in range(height):
            for x in range(left, right):
                if random.random() < 0.1 and y > 1:
                    # wall 'X'
                    if new_genome[y][x] == 'X': 
                        if new_genome[y-1][x] != 'X':
                            genome[y][x] = random.choices(['B', '-'], weights=[1, 3], k=1)[0]
                    # pipe segment/pipe top '|', 'T'
                    elif new_genome[y][x] == '|' or new_genome[y][x] == 'T': 
                        if new_genome[y-1][x] != '|' and y != height and (new_genome[y+1][x] != '|' or new_genome[y+1][x] != 'T'):
                            # increased weight for coin block '?'
                            genome[y][x] = random.choices(['M', '?'], weights=[1, 3], k=1)[0]
                    elif new_genome[y][x] == '-':
                        # reduced number of random calls
                        choice = random.random()
                        if choice <= 0.3:
                            genome[y][x] = '?'
                        elif choice >= 0.6:
                            genome[y][x] = 'o'
        return genome

    # Create zero or more children from self and other
    def generate_children(self, other):
        new_genome = copy.deepcopy(self.genome)
        other_genome = copy.deepcopy(other.genome)
        # Leaving first and last columns alone...
        # do crossover with other
        left = 1
        right = width - 1
        for y in range(height):
            for x in range(left, right):
                # STUDENT Which one should you take?  Self, or other?  Why?
                # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
                if random.random() < 0.5:
                    new_genome[y][x] = other_genome[y][x] if other_genome[y][x] != 'T' and other_genome[y][x] != '|' else new_genome[y][x]
        
        # do mutation; note we're returning a one-element tuple here
        mutation_rate = 0.1 
        for y in range(height): 
            for x in range(left, right): 
                if random.random() < mutation_rate: 
                    new_genome[y][x] = random.choice(options)

        return (Individual_Grid(new_genome),)

    # Turn the genome into a level string (easy for this genome)
    def to_level(self):
        return self.genome

    # These both start with every floor tile filled with Xs
    # STUDENT Feel free to change these
    @classmethod
    def empty_individual(cls):
        g = [["-" for col in range(width)] for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        g = [random.choices(options, k=width) for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        g[8:14][-1] = ["f"] * 6
        g[14:16][-1] = ["X", "X"]
        return cls(g)
    
def generate_successors(population):
    results = []
    # STUDENT Design and implement this
    # Hint: Call generate_children() on some individuals and fill up results.

    # selection = random.randint(0, 1)
    selection = 0

    # elitist selection strategy
    if selection == 0: 
        # print('elitist')
        elitism_rate = 0.1  # Adjust this value based on your preferences
        elite_count = int(elitism_rate * len(population))
        elites = sorted(population, key=lambda x: x.fitness(), reverse=True)[:elite_count]

        results = elites[:]  # Add elites to the new population

        # Generate offspring for the rest of the population using elitist selection
        while len(results) < len(population):
            parent1 = random.choice(elites)
            parent2 = random.choice(elites)

            if Individual == Individual_Grid:
                child1 = parent1.generate_children(parent2)[0]
                child2 = parent2.generate_children(parent1)[0]
                results.extend([child1])
                results.extend([child2])
            else: 
                if len(parent1.genome) > 0 and len(parent2.genome) > 0:
                    child1, child2 = parent1.generate_children(parent2)
                    results.extend([child1])
                    results.extend([child2])

    # roulette wheel selection strategy 
    else: 
        # print('roulette')
        total_fitness = sum(individual.fitness() for individual in population)

        # Select parents and generate children
        while len(results) < len(population):
            # Roulette wheel selection
            rand = random.random() * total_fitness
            cumulative_probability = 0
            parent1 = None
            parent2 = None
            for individual in population:
                cumulative_probability += individual.fitness()
                if cumulative_probability >= rand:
                    if parent1 is None:
                        parent1 = individual
                    elif parent2 is None:
                        parent2 = individual
                        break
            if parent1 != None and parent2 != None: 
                if Individual == Individual_Grid: 
                    child1 = parent1.generate_children(parent2)[0]
                    child2 = parent2.generate_children(parent1)[0]
                    results.extend([child1])
                    results.extend([child2])
                else: 
                    if len(parent1.genome) > 0 and len(parent2.genome) > 0:
                        child1, child2 = parent1.generate_children(parent2)
                        results.extend([child1])
                        results.extend([child2])

    return results


def ga():
    # STUDENT Feel free to play with this parameter
    pop_limit = 480
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print("It's ideal if pop_limit divides evenly into " + str(batches) + " batches.")
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()
        # STUDENT (Optional) change population initialization
        population = [Individual.random_individual() if random.random() < 0.9
                      else Individual.empty_individual()
                      for _g in range(pop_limit)]
        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness,
                              population,
                              batch_size)
        init_done = time.time()
        print("Created and calculated initial population statistics in:", init_done - init_time, "seconds")
        generation = 0
        start = time.time()
        now = start
        print("Use ctrl-c to terminate this loop manually.")
        try:
            while True:
                now = time.time()
                # Print out statistics
                if generation > 0:
                    best = max(population, key=Individual.fitness)
                    print("Generation:", str(generation))
                    print("Max fitness:", str(best.fitness()))
                    print("Average generation time:", (now - start) / generation)
                    print("Net time:", now - start)
                    with open("levels/last.txt", 'w') as f:
                        for row in best.to_level():
                            f.write("".join(row) + "\n")
                generation += 1
                # STUDENT Determine stopping condition
                stop_condition = False if generation <= 10 else True
                if stop_condition:
                    break
                # STUDENT Also consider using FI-2POP as in the Sorenson & Pasquier paper
                gentime = time.time()
                next_population = generate_successors(population)
                gendone = time.time()
                print("Generated successors in:", gendone - gentime, "seconds")
                # Calculate fitness in batches in parallel
                next_population = pool.map(Individual.calculate_fitness,
                                           next_population,
                                           batch_size)
                popdone = time.time()
                print("Calculated fitnesses in:", popdone - gendone, "seconds")
                population = next_population
        except KeyboardInterrupt:
            pass
    return population


if __name__ == "__main__":
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    now = time.strftime("%m_%d_%H_%M_%S")
    # STUDENT You can change this if you want to blast out the whole generation, or ten random samples, or...
    for k in range(0, 10):
        with open("levels/" + now + "_" + str(k) + ".txt", 'w') as f:
            for row in final_gen[k].to_level():
                f.write("".join(row) + "\n")