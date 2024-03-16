import copy
import multiprocessing.pool as mpool
import os
import random
import time
import math
import json


DANCE_DIRECTORY = 'output_videos_jsons\\insane'
IDEAL_POSE_DIRECTORY = 'ideal_poses\\jsons'

face = [0, 15, 16, 17, 18]
r_foot = [11, 22, 23, 24]
l_foot = [14, 19, 20, 21]
hips = [8, 9, 12]

'''
Representing the genome
'''
def Load_Poses(dir):
    dance_poses = []

    for filename in os.listdir(dir):
        f = os.path.join(dir, filename)
        # print(f)

        with open(f, 'r') as json_file:
            pose_data = json.load(json_file)

        # print(pose_data)
        dance_poses.append(pose_data)

    return dance_poses


'''
THIS CODE WAS TAKEN AND MODIFIED FROM ASSIGNMENT P5 OF CMPM 146: GAME AI, SPRING 2024
'''

class Individual_Dance(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None
    
    '''CALCULATES THE FITNESS OF A DANCE'''
    def calculate_fitness(self):
        # CALCULATE THE FITNESS BY CHECKING SIMILARITY TO "DESIRABLE" POSE DATA
        points = 0
        
        for gpose_frame in self.genome:
            for ipose in ideal_poses:
                # A pose is a dictionary; important keypoints are 0-14

                keypoints_self = gpose_frame['people'][0]["pose_keypoints_2d"]
                x_coords_self = keypoints_self[0::3]
                y_coords_self = keypoints_self[1::3]
                # c_vals_self = keypoints_self[2::3]

                keypoints_ideal = ipose['people'][0]["pose_keypoints_2d"]
                x_coords_ideal = keypoints_ideal[0::3]
                y_coords_ideal = keypoints_ideal[1::3]
                # c_vals_ideal = keypoints_ideal[2::3]
                for i in range(15):
                    x1 = x_coords_self[i]
                    y1 = y_coords_self[i]
                    x2 = x_coords_ideal[i]
                    y2 = y_coords_ideal[i]
                    
                    points += 1 - math.dist((x1,y1), (x2,y2))
   
        self._fitness = points

    '''Return the cached fitness value or calculate it as needed.'''
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness
    
    '''Mutate a genome into a new genome.  Note that this is a _genome_, not an individual!'''
    def mutate(self, genome):
        # MUTATE BY SHIFTING KEYPOINTS TO NEW LOCATIONS
        # DO THIS RANDOMLY OR IN A STRUCTURED WAY (arms & legs shift by a lot, torso points move by a little bit, etc.)
        # READ DOCUMENTATION TO SEE WHICH KEYPOINT CORRESPONDS TO WHICH BODY PART
        for gpose_frame in genome:
            keypoints_self = gpose_frame['people'][0]["pose_keypoints_2d"]
            x_coords = keypoints_self[0::3]
            y_coords = keypoints_self[1::3]
            c_vals = keypoints_self[2::3]

            # Change the pose somehow
            mutation_offset = 0.05
            mutated_points = []
            for i in range(25):
                if (c_vals[i] != 0 and i not in mutated_points):
                    x_offset = (random.random() * 2 * mutation_offset) - mutation_offset
                    y_offset = (random.random() * 2 * mutation_offset) - mutation_offset

                    if (i in face):
                        for j in face:
                            x_coords[j] += x_offset
                            y_coords[j] += y_offset
                            mutated_points.append(j)
                    elif (i in r_foot):
                        for j in r_foot:
                            x_coords[j] += x_offset
                            y_coords[j] += y_offset
                            mutated_points.append(j)
                    elif (i in l_foot):
                        for j in l_foot:
                            x_coords[j] += x_offset
                            y_coords[j] += y_offset
                            mutated_points.append(j)
                    elif (i in hips):
                        for j in hips:
                            x_coords[j] += x_offset
                            y_coords[j] += y_offset
                            mutated_points.append(j)
                    else:
                        x_coords[i] += x_offset
                        y_coords[i] += y_offset
                        mutated_points.append(j)
        return genome

    '''COPYING CROSSOVER METHOD FROM P5'''
    def generate_children(self, other):
        pa = random.randint(0, len(self.genome) - 1)
        pb = random.randint(0, len(other.genome) - 1)
        a_part = self.genome[:pa] if len(self.genome) > 0 else []
        b_part = other.genome[pb:] if len(other.genome) > 0 else []
        ga = a_part + b_part
        b_part = other.genome[:pb] if len(other.genome) > 0 else []
        a_part = self.genome[pa:] if len(self.genome) > 0 else []
        gb = b_part + a_part
        # do mutation
        # return Individual_Dance(self.mutate(ga)), Individual_Dance(self.mutate(gb))
        '''
        I don't understand what the original does
        '''
        # length 2 tuple of 2 new individuals
        return [Individual_Dance(self.mutate(ga)), Individual_Dance(self.mutate(gb))]
    
        return Individual_Dance(Individual_Dance(ga).mutate(gb))

    
    '''
    RETURNS LIST OF POSE PER FRAME DATA REPRESENTING THE DANCE
    EACH ELEMENT IS A DICTIONARY WITH THE KEYPOINTS OF A POSE IN A GIVEN FRAME OF THE DANCE VIDEO
    READ DOCUMENTATION TO SEE WHICH KEYPOINT CORRESPONDS TO WHICH BODY PART
    '''
    def get_dance(self):
        return self.genome
    
    # @classmethod
    # def base_individual():
    #     return Individual_Dance(Load_Dance_Genome())
    
'''
The following is a copy paste of the selection algorithms used in my P5
The 1st uses Roulette wheel selection
The 2nd uses an Elitist random selection
'''

def generate_successors(population):
    results = []
    # STUDENT Design and implement this
    # Hint: Call generate_children() on some individuals and fill up results.

    
    # STRATEGY: Roulette wheel selection
    fits = [1.1**individual.fitness() for individual in population]
    total_fit = sum(fits)

    for i in range(480/2):
        # roulette selecting parent 1
        parent1 = None
        selector = random.uniform(0, total_fit)
        fit_pointer = 0
        for individual in population:
            fit_pointer += 1.1**individual.fitness()
            if selector <= fit_pointer:
                # add individual to results
                parent1 = individual
                break

        # roulette selecting parent 2
        parent2 = None
        selector = random.uniform(0, total_fit)
        fit_pointer = 0
        for individual in population:
            fit_pointer += 1.1**individual.fitness()
            if selector <= fit_pointer:
                # add individual to results
                parent2 = individual
                break
        
        child_1, child_2 = parent1.generate_children(parent2)
        results.append(child_1)
        results.append(child_2)
    

    return results

    
'''
def generate_successors(population):
    results = []
    # STUDENT Design and implement this
    # Hint: Call generate_children() on some individuals and fill up results.

    # strategy: Random selection with Elitism

    # Top x percent in fitness guaranteed on to next generation
    percentage_to_be_elite = 0.1
    
    # Guarantee the Elites
    n_elites = int(percentage_to_be_elite * len(population))
    sorted_population = sorted(population, key=lambda individual: individual.fitness(), reverse=True)
    for i in range(len(sorted_population)):
        if i > n_elites:
            break

        results.append(sorted_population[i])

    # The rest are random children
    for i in range(len(population)-n_elites):
        parent1 = random.choice(population)
        parent2 = random.choice(population)

        new = parent1.generate_children(parent2)[0]
        results.append(new)

    return results
'''

Individual = Individual_Dance

'''
The following is a copy paste of the genetic algorithm from PA
'''

def ga():
    # STUDENT Feel free to play with this parameter
    # THIS SEEMS TO BE THE SIZE OF THE POPULATION
    pop_limit = 480
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print("It's ideal if pop_limit divides evenly into " + str(batches) + " batches.")
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()

        '''
        INITIALIZATION OF POPULATION
        THE INITIAL POPULATION WILL JUST BE {pop_limit} CLONES OF THE ORIGINAL DANCE
        '''

        # population = [Individual.random_individual() if random.random() < 0.9
        #               else Individual.empty_individual()
        #               for _g in range(pop_limit)]

        # ABOVE CODE IS THE ORIGINAL INITIALIZATION FOR P5
        # WRITE NEW INITIALIZATION HERE
        


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

                    '''
                    THIS NEEDS TO WRITE TO A NEW DIRECTORY AND MAKE NEW FOLDERS WITH ALL THE NEW JSON FILES OF THE BEST DANCE
                    '''

                    # with open("levels/last.txt", 'w') as f:
                    #     for row in best.to_level():
                    #         f.write("".join(row) + "\n")

                    # ABOVE CODE IS THE ORIGINAL P5 FILE GENERATION
                    # WRITE NEW CODE TO GENERATE FOLDERS CONTAINING GENERATED POSE JSON FILES



                generation += 1
                '''
                STOPS GENERATING AFTER 10 GENERATIONS
                '''
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

'''
The following is a partial copy of P5's main function
'''

if __name__ == "__main__":
    # Load the base dance from files
    base_dance = Load_Poses(DANCE_DIRECTORY)
    ideal_poses = Load_Poses(IDEAL_POSE_DIRECTORY)

    test_individual = Individual_Dance(base_dance)
    test_individual_2 = Individual_Dance(base_dance)
    test_genome = test_individual.get_dance()

    # for i in range(len(test_genome)):
    #     print("frame ", i)
    #     print(test_genome[i])

    
    # for i in range(len(ideal_poses)):
    #     print("pose ", i+1)
    #     print(ideal_poses[i])

    print("Test individual fitness: ", test_individual.fitness())
    print("Test individual 2 fitness: ", test_individual.fitness())

    child_1, child_2 = test_individual.generate_children(test_individual_2)

    print("child 1 fitness: ", child_1.fitness())
    print("child 2 fitness: ", child_2.fitness())


    '''
    This part is supposed to start the generation
    '''
    # final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    # best = final_gen[0]
    # print("Best fitness: " + str(best.fitness()))
    # now = time.strftime("%m_%d_%H_%M_%S")

    print("Done")