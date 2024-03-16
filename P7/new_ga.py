import copy
import multiprocessing.pool as mpool
import matplotlib.pyplot as plt
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

# Create a list of connections between keypoints to form the skeleton
connections = [
    (0, 1), (1, 2), (1, 5), (1, 8),         # Torso
    (8, 9), (8, 12),                        # Hips
    (2, 3), (3, 4),                         # Right Arm
    (5, 6), (6, 7),                         # Left Arm
    (9, 10), (10, 11),                      # Right Leg
    (12, 13), (13, 14),                     # Left Leg
    (0, 15), (15, 17), (0, 16), (16, 18),   # Face
    (14, 21), (14, 19), (19, 20),           # Left Foot
    (11, 24), (11, 22), (22, 23)            # Right Foot
]

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

# Load the base dance from files
base_dance = Load_Poses(DANCE_DIRECTORY)
ideal_poses = Load_Poses(IDEAL_POSE_DIRECTORY)

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
        return self

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
            mutation_offset = 0.1
            mutation_chance = 0.8
            mutated_points = []
            for i in range(25):
                if (c_vals[i] != 0 and i not in mutated_points and random.random() < mutation_chance):
                    x_offset = (random.random() * 2 * mutation_offset) - mutation_offset
                    y_offset = (random.random() * 2 * mutation_offset) - mutation_offset

                    # Move the face points together
                    if (i in face):
                        for j in face:
                            x_coords[j] += x_offset
                            y_coords[j] += y_offset
                            mutated_points.append(j)
                    # Move the right foot points together
                    elif (i in r_foot):
                        for j in r_foot:
                            x_coords[j] += x_offset
                            y_coords[j] += y_offset
                            mutated_points.append(j)
                    # Move the left foot points together
                    elif (i in l_foot):
                        for j in l_foot:
                            x_coords[j] += x_offset
                            y_coords[j] += y_offset
                            mutated_points.append(j)
                    # Move the hips points together
                    elif (i in hips):
                        for j in hips:
                            x_coords[j] += x_offset
                            y_coords[j] += y_offset
                            mutated_points.append(j)
                    else:
                        x_coords[i] += x_offset
                        y_coords[i] += y_offset
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
    
    '''
    RETURNS LIST OF POSE PER FRAME DATA REPRESENTING THE DANCE
    EACH ELEMENT IS A DICTIONARY WITH THE KEYPOINTS OF A POSE IN A GIVEN FRAME OF THE DANCE VIDEO
    READ DOCUMENTATION TO SEE WHICH KEYPOINT CORRESPONDS TO WHICH BODY PART
    '''
    def get_dance(self):
        return self.genome
    
    @classmethod
    def base_individual(cls):
        return cls(base_dance)
    
'''
The following is a copy paste of the selection algorithms used in my P5
The 1st uses Roulette wheel selection
The 2nd uses an Elitist random selection
'''


# def generate_successors(population):
#     results = []
#     # STUDENT Design and implement this
#     # Hint: Call generate_children() on some individuals and fill up results.
    
#     # STRATEGY: Roulette wheel selection
#     fits = [1.1**individual.fitness() for individual in population]
#     total_fit = sum(fits)

#     for i in range(480/2):
#         # roulette selecting parent 1
#         parent1 = None
#         selector = random.uniform(0, total_fit)
#         fit_pointer = 0
#         for individual in population:
#             fit_pointer += 1.1**individual.fitness()
#             if selector <= fit_pointer:
#                 # add individual to results
#                 parent1 = individual
#                 break

#         # roulette selecting parent 2
#         parent2 = None
#         selector = random.uniform(0, total_fit)
#         fit_pointer = 0
#         for individual in population:
#             fit_pointer += 1.1**individual.fitness()
#             if selector <= fit_pointer:
#                 # add individual to results
#                 parent2 = individual
#                 break
        
#         child_1, child_2 = parent1.generate_children(parent2)
#         results.append(child_1)
#         results.append(child_2)
    

#     return results

    

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
    # for i in range(len(population)-n_elites):
    while len(results) < len(population):
        parent1 = random.choice(population)
        parent2 = random.choice(population)

        child_1, child_2 = parent1.generate_children(parent2)
        if random.random() < 0.5:
            results.append(child_1)
        else:
            results.append(child_2)

    return results


Individual = Individual_Dance

'''
The following is a copy paste of the genetic algorithm from PA
'''

def ga():
    # STUDENT Feel free to play with this parameter
    # THIS SEEMS TO BE THE SIZE OF THE POPULATION
    pop_limit = 16
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
        # NEW INITIALIZATION OF POPULATION
        population = [Individual.base_individual() for _ in range(pop_limit)]

        # for i in range(len(population)):
        #     print("individual ", i, ":")
        #     print(population[i].fitness())

        # print(population)

        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness,
                              population,
                              batch_size)
        
        # print(population)
        
        # for i in range(len(population)):
        #     print("individual ", i, ":")
        #     print(population[i].fitness())

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
                    # WRITE NEW CODE TO GENERATE FOLDERS CONTAINING GENERATED POSE JSON FILES
                    generate_dance_frames(best, generation)
                generation += 1
                '''
                STOPS GENERATING AFTER 10 GENERATIONS
                '''
                stop_condition = generation > 10
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

def generate_dance_frames(best_individual, gen):
    for _ in range(10):
        frame = random.randint(0,800)
        keypoints = best_individual.get_dance()[frame]['people'][0]['pose_keypoints_2d']

        # Extract x and y coordinates and confidence values
        x_coords = keypoints[0::3]
        y_coords = keypoints[1::3]
        c_vals = keypoints[2::3]

        # Plot skeleton
        plt.scatter(x_coords, y_coords, c="red")  # Plot keypoints

        for connection in connections:
            p1, p2 = connection
            if (c_vals[p1] != 0 and c_vals[p2] != 0):
                plt.plot([x_coords[connection[0]], x_coords[connection[1]]],
                        [y_coords[connection[0]], y_coords[connection[1]]], c="blue")  # Connect keypoints

        plt.ylim(0,0.85)
        plt.xlim(0,2)
        plt.gca().invert_yaxis()  # Invert y-axis to match image coordinates
        
        # Save plot as png
        fname = ".\\dance_generations\\gen" + str(gen) + "\\frame_" + str(frame) + ".png"
        plt.savefig(fname)
        plt.clf()

'''
The following is a partial copy of P5's main function
'''

if __name__ == "__main__":
    

    # test_individual = Individual_Dance(base_dance)
    # test_individual_2 = Individual_Dance(base_dance)
    # test_genome = test_individual.get_dance()

    # for i in range(len(test_genome)):
    #     print("frame ", i)
    #     print(test_genome[i])

    
    # for i in range(len(ideal_poses)):
    #     print("pose ", i+1)
    #     print(ideal_poses[i])

    # print("Test individual fitness: ", test_individual.fitness())
    # print("Test individual 2 fitness: ", test_individual.fitness())

    # child_1, child_2 = test_individual.generate_children(test_individual_2)

    # print("child 1 fitness: ", child_1.fitness())
    # print("child 2 fitness: ", child_2.fitness())


    '''
    This part is supposed to start the generation
    '''
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    now = time.strftime("%m_%d_%H_%M_%S")

    print("Done")