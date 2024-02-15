Cromwell De Guzman (cgdeguzm) and Beatrice Yu (besyu)

# ENCODING 1 - Grid Encoding
- Implement generate_successors using at least two selection strategies to build up the next population

    - The function, generate_successors, is responsible for creating the next generation of individuals in the population. It randomly picks between two selection methods: elitist selection and roulette wheel selection. Elitist selection involves sorting the population by fitness and selecting two of the most fit individuals which are then passed to the generate_children function. Roulette wheel selection involves giving each individual a probability of being selected based on fitness. Those with higher fitness will have a higher chance of being selected. Two individuals are selected and passed to the generate_children function. 

- Implement crossover in generate_children for the Grid encoding

    - We chose to use uniform crossover. It randomly chooses from either parent for each gene. However, there are constraints to prevent certain tiles from being switched, like pipes. 

- Implement mutation in mutate for the Grid encoding

    - The function, mutate, applies mutations to the genome. It changes the content of the genome based on certain conditions and probabilities, such as there being a higher chance of selecting an empty space. Additionally, floating walls and pipes may be replaced. 
    - We chose to have a 10% chance of mutation happening. This makes it so that mutation does not occur too frequently. 

# ENCODING 2 - Design Element Encoding

- Switch the encoding to Individual_DE and explore its outputs

    - The crossover function is responsible for creating children from two parent genomes using variable point crossover. It selects random indices in each parent genome and divides each genome into two sections using a random index. It then returns two children, one with the front section of parent a and the back section of parent b and the other with the front section of parent b and the back section of parent a. 
    - The mutate function is responsible for mutating an individual's genome. It randomly selects a design element from the genome and modifies it based on certain probabilities. 

- Improve the fitness function and mutation operator (and potentially crossover) in Individual_DE

# SUMMARY

- Pick 1 favorite level from either encoding

    - Our favorite level was...

- Play that level in the Unity player and make sure you can beat it

    - Yes, the level is beatable.