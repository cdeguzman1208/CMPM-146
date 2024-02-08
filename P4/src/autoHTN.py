import pyhop
import json
import time

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

'''
make_method():
This function dynamically creates a method for a particular crafting recipe. It generates a
method that ensures all necessary requirements are met before executing the associated
operator.
'''
def make_method (name, rule):
	def method (state, ID):
		# your code here
		condition = []
		for key, value in rule.items():
			if key != 'Produces':
				if type(value) == dict:
					for k, v in reversed(value.items()):
						condition.append(('have_enough', ID, k, v))
		condition.append(('op_' + name, ID))
		return condition
	method.__name__ = name
	return method

'''
declare_methods():
This function organizes and declares methods for each crafting recipe in the provided data. It
sorts the recipes by the time it takes to produce the item and creates methods for each one
using make_method.
'''
def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	
	method_dict = {}
	for key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=True):
		key = key.replace(' ', '_')
		for name_of_produce in value['Produces'].items():
			if name_of_produce in method_dict:
				if isinstance(method_dict[name_of_produce], list):
					my_method = make_method(key, value)
					method_dict[name_of_produce].append(my_method)
				else:
					method_dict[name_of_produce] = [method_dict[name_of_produce]]
			else:
				my_method = make_method(key, value)
				method_dict[name_of_produce] = [my_method]
	for name, method in method_dict.items():
		pyhop.declare_methods('produce_' + name[0], *method)

'''
make_operator():
This function generates an operator function for a given crafting recipe. It is used to define the
effect of executing a particular recipe on the state.
'''
def make_operator (rule):

	def operator (state, ID):
		# your code here
		# CHECK LOOP
		for key, value in rule.items():
			if key == 'Requires':
				for k, v in value.items():
					if getattr(state, k)[ID] < v:
						return False
			if key == 'Consumes':
				for k, v in value.items():
					if getattr(state, k)[ID] < v:
						return False
			if key == 'Time':
				if state.time[ID] < value:
					return False

		
		# CHANGE STATE LOOP
		for key, value in rule.items():
			if key == 'Produces':
				for k, v in value.items():
					setattr(state, k, {ID: getattr(state, k)[ID] + v})
					# Add tool to made state
					if hasattr(state, 'made_'+k):
						setattr(state, 'made_'+k, {ID: True})
			if key == 'Consumes':
				for k, v in value.items():
					setattr(state, k, {ID: getattr(state, k)[ID] - v})
			if key == 'Time':
				state.time[ID] -= value


		return state
	

	return operator

'''
declare_operators():
This function organizes and declares operators for each crafting recipe in the provided data. It
creates operators for each recipe using make_operator.
'''
def declare_operators (data):
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
	operator_list = []
	for key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=True):
		key = key.replace(' ', '_')
		operator_temp = make_operator(value)
		time_for_oper = value['Time']
		operator_temp.__name__ = 'op_' + key
		operator_list.append((operator_temp, time_for_oper))
		sorted(operator_list, key=lambda time: time_for_oper, reverse=False)
	for oper, times in operator_list:
		pyhop.declare_operators(oper)

'''
add_heuristic():
This function adds a heuristic to the planning process. The heuristic prunes search branches
based on whether a task has already been executed.
'''
def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	'''def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
		if depth > 45:
			return True
		return False
	pyhop.add_check(heuristic)'''

	# Checks to see if tool has already been made and prunes if it has
	def heuristic2 (state, curr_task, tasks, plan, depth, calling_stack):
		item = curr_task[0][9:] # This gets a substring without the 'produce_' part
		if item in data['Tools'] and getattr(state, 'made_'+item)[ID]:
			return True
		return False
	pyhop.add_check(heuristic2) 

'''
set_up_state():
This function initializes the initial state for the planning problem. It creates a Pyhop state
object, sets initial quantities for items and tools, and sets the initial time.
'''
def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})
		setattr(state, 'made_' + item, {ID: False})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

'''
set_up_goals():
This function sets up the goals for the planning problem based on the provided data.
'''
def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=250) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	# pyhop.print_operators()
	# pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	# pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)

	'''Required tests'''
	
	# TEST 1
	# pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 1)], verbose=3)
	'''pass'''

	# RANDOM TEST
	# pyhop.pyhop(state, [('have_enough', 'agent', 'bench', 1), ('have_enough', 'agent', 'stick', 2), ('have_enough', 'agent', 'plank', 3)], verbose=3)
	
	# TEST 2
	# pyhop.pyhop(state, [('have_enough', 'agent', 'wooden_pickaxe', 1)], verbose=3)
	'''pass'''

	# TEST 3
	# pyhop.pyhop(state, [('have_enough', 'agent', 'furnace', 1)], verbose=3)
	'''pass'''

	# TEST 4
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1)], verbose=3)
	'''pass'''

	# TEST 5
	# state.plank = {'agent': 1}
	# pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 1)], verbose=3)
	'''pass'''

	# TEST 6
	# state.plank = {'agent': 3}
	# state.stick = {'agent': 2}
	# pyhop.pyhop(state, [('have_enough', 'agent', 'wooden_pickaxe', 1)], verbose=3)
	'''pass'''

	# TEST 7
	# pyhop.pyhop(state, [('have_enough', 'agent', 'stone_pickaxe', 1)], verbose=3)
	'''pass'''

	# TEST 8
	# pyhop.pyhop(state, [('have_enough', 'agent', 'iron_pickaxe', 1)], verbose=3)
	'''Max recursion depth'''

	# TEST 9
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 10)], verbose=3)
	'''Max recursion depth'''

	# Test 10
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
	'''Max recursion depth'''