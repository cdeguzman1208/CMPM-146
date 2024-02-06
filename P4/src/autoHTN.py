import pyhop
import json

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
This implementation creates a method that checks requirements based on the input rule by
iterating over the key-value pairs. It generates a list of conditions (condition) and includes the
operation itself in the list. The method is named based on the input name.
'''
def make_method (name, rule):
	def method (state, ID):
		# your code here
		condition = []
		for key, value in rule.items():
			if key != 'Produces':
				if type(value) == dict:
					for k, v in value.items():
						condition.append(('have_enough', ID, k, v))
		condition.append(('op_' + name, ID))
		return condition
	method.__name__ = name
	return method

'''
declare_methods():
This implementation creates a method table (method_table) where each entry corresponds to a
produced item, and the associated value is a list of tuples containing the method and its associated
time. The methods are sorted based on time within each produce category. Finally, the methods are
declared using pyhop.declare_methods.
'''
def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	
	recipes = data['Recipes']
	method_table = {}
	for r in recipes:
		name = r.replace(' ', '_')
		method = make_method(name, recipes[r])
		r_data = recipes[r]
		produce = list(r_data['Produces'])[0]
		
		if produce not in method_table:
			method_table[produce] = []
		m_tuple = (method, r_data['Time'])
		method_table[produce].append(m_tuple)
		method_table[produce].sort(key=lambda s: s[1])
		
	for i in method_table:
		name = 'produce_' + i
		for j in method_table[i]:
			pyhop.declare_methods(name, j[0])

'''
make_operator():
This implementation creates an operator function that modifies the state based on the input
rule. It iterates through the keys of the rule and updates the state accordingly. The operator is
unnamed.
'''

# Does the state change even if the requirements aren't satisfied?

def make_operator (rule):
	def operator (state, ID):
		# your code here
		for key, value in rule.items():
			if key == 'Produces':
				for k, v in value.items():
					setattr(state, k, {ID: getattr(state, k)[ID] + v})
			if key == 'Consumes':
				for k, v in value.items():
					if getattr(state, k)[ID] >= v:
						setattr(state, k, {ID: getattr(state, k)[ID] - v})
					# Added to check if not enough items
					else:
						return False
			if key == 'Time':
				if state.time[ID] >= v:
					state.time[ID] -= v
				else:
					return False
		return state
	return operator

'''
declare_operators():
This implementation declares operators by calling make_operator on each recipe and appending
the resulting operator to a list (r_list). It then iterates through this list and declares each operator
using pyhop.declare_operators(op).
'''
def declare_operators (data):
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
	recipes = data['Recipes']
	r_list = []
	for r in recipes:
		name = r.replace(' ', '_')
		op = make_operator(recipes[r])
		op.__name__ = 'op_' + name
		r_list.append(op)
		
	for op in r_list:
		pyhop.declare_operators(op)

def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
		# your code here
		return False # if True, prune this branch

	pyhop.add_check(heuristic)

def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=300) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	pyhop.print_operators()
	pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	# pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)

	# pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 1)], verbose=3)
