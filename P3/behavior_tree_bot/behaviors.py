import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

# attacks "weakest" enemy planet by factoring each enemy planets' number of ships, growth rate, and distance from each friendly planet
def attack_weakest_enemy_planet(state):
    src_planet = None
    dst_planet = None
    min_cost = 10000
    for my_planet in state.my_planets():
        for enemy_planet in state.enemy_planets():
            distance = state.distance(my_planet.ID, enemy_planet.ID)
            cost = enemy_planet.num_ships + (distance * enemy_planet.growth_rate) + 1
            if cost < min_cost and cost < my_planet.num_ships:
                if enemy_planet.ID not in [fleet.destination_planet for fleet in state.my_fleets()]:
                    min_cost = cost
                    src_planet = my_planet
                    dst_planet = enemy_planet
    
    if not src_planet or not dst_planet:
        return False
    else:
        return issue_order(state, src_planet.ID, dst_planet.ID, min_cost)

# spreads to weakest neutral planet, if any friendly planet has enough ships to send to it
def spread_to_weakest_neutral_planet(state):  
    src_planet = None
    dst_planet = None
    min_cost = 10000
    for my_planet in state.my_planets():
        for neutral_planet in state.neutral_planets():
            cost = neutral_planet.num_ships + 1
            if cost < min_cost and cost < my_planet.num_ships:
                if neutral_planet.ID not in [fleet.destination_planet for fleet in state.my_fleets()]:
                    min_cost = cost
                    src_planet = my_planet
                    dst_planet = neutral_planet

    if not src_planet or not dst_planet:
        return False
    else:
        return issue_order(state, src_planet.ID, dst_planet.ID, min_cost)