from lib.gopherpysat import Gophersat
from typing import Dict, Tuple, List, Union
import itertools
import random
import time
import sys

gophersat_exec = "./lib/gophersat-1.1.6"

# Generate all the voca needed for the SAT solver
# A symbol reprensents the precense (or not) of one number at the given (i, j) position
# Format : 1_i_j , 2__i_j , 3_i_j ... 9_i_j with i and j belong to [0..8]
def generate_voca () -> List : 
	res = []

	for number in range(1, 10) :
		for i in range(0, 9) :
			for j in range(0, 9) :
				res.append(f"{number}_{i}_{j}")

	return res

# 1_i_j <-> non(2_i_j) ET non(3_i_j) ET ... non(9_i_j)
# Ce qui devient : 
# 1_i_j OU 2_i_j OU 3_i_j OU ... OU 9_i_j
# ET
# non(1_i_j) OU non(2_i_j) ET non(1_i_j) OU non(3_i_j) ET ... ET non(1_i_j) OU non(9_i_j) 
def insert_only_one_number_in_case (gs:Gophersat, voca:List) :
	
	for case in voca :
		num_case = int(case.split('_')[0])
		i  = case.split('_')[1]
		j  = case.split('_')[2]

		ou_clause = [case]
		for number in range(1, 10) : # non(1_i_j) OU non(2_i_j) ET non(1_i_j) OU non(3_i_j) ET ... ET non(1_i_j) OU non(9_i_j) 			
			if num_case != number :
				ou_clause.append(f"{number}_{i}_{j}")	
				gs.push_pretty_clause([f"-{case}", f"-{number}_{i}_{j}"])

		gs.push_pretty_clause(ou_clause)
		ou_clause = []

# 1_i_j <-> non(1_i_0) ET non(1_i_2) ET non(1_i_3) ET ... ET non(1_i_8) 
def insert_one_value_in_row(gs:Gophersat, voca:List) :

	for case in voca :
		num_case = case.split('_')[0]
		i  = case.split('_')[1]
		j  = int(case.split('_')[2])

		ou_clause = [case]
		for j_prime in range(0, 9) : # non(1_i_j) OU non(1_i_0) ET non(1_i_j) OU non(1_i_1) ET ... ET non(1_i_j) OU non(1_i_8) 			
			if j != j_prime :
				ou_clause.append(f"{num_case}_{i}_{j_prime}")	
				gs.push_pretty_clause([f"-{case}", f"-{num_case}_{i}_{j_prime}"])

		gs.push_pretty_clause(ou_clause)
		ou_clause = []

# 1_i_j <-> non(1_0_j) ET non(1_1_j) ET non(1_2_j) ET ... ET non(1_3_j) 
def insert_one_value_in_col(gs:Gophersat, voca:List) :
	
	for case in voca :
		num_case = case.split('_')[0]
		i  = int(case.split('_')[1])
		j  = case.split('_')[2]

		ou_clause = [case]
		for i_prime in range(0, 9) : # non(1_i_j) OU non(1_1_j) ET non(1_i_j) OU non(1_2_j) ET ... ET non(1_i_j) OU non(1_8_j) 			
			if i != i_prime :
				ou_clause.append(f"{num_case}_{i_prime}_{j}")	
				gs.push_pretty_clause([f"-{case}", f"-{num_case}_{i_prime}_{j}"])

		gs.push_pretty_clause(ou_clause)
		ou_clause = []

# i^b = 3 x (i//3)
# j^b = 3 x (j//3)
# 1_i_j <-> non(1_ib_jb) ET non(1_ib+1_jb) ET non(1_ib+2_jb) ET ... ET non(1_ib+2_jb+2)
def insert_one_value_in_square(gs:Gophersat, voca:List) :
	for case in voca :
		num_case = case.split('_')[0]
		i  = int(case.split('_')[1])
		j  = int(case.split('_')[2])

		ib = 3*(i//3) # coordinates of the first case of the square
		jb = 3*(j//3)

		ou_clause = [case]
		for i_prime in range(ib, ib+3) :
			for j_prime in range(jb, jb+3) :
				if i != i_prime or j != j_prime :

					ou_clause.append(f"{num_case}_{i_prime}_{j_prime}")	
					gs.push_pretty_clause([f"-{case}", f"-{num_case}_{i_prime}_{j_prime}"])

		gs.push_pretty_clause(ou_clause)
		ou_clause = []

def insert_rules(gs, voc) :
	insert_only_one_number_in_case(gs, voc)
	insert_one_value_in_row(gs, voc)
	insert_one_value_in_col(gs, voc)
	insert_one_value_in_square(gs, voc)

# starting function of recursive backtracking
# and return the resolved sudoku
def generate_random_sudoku(gs:Gophersat) -> List :

	coord_list = [(0, 0) for i in range(81)] # we create a list of all coord

	for i in range(9) :
		for j in range(9) :
			coord_list[(i*9)+j] = (i, j)

	sudoku = [[0 for x in range(9)] for y in range(9)]
	sudoku_filled = insert_values_in_sudoku(gs, coord_list, sudoku)

	if sudoku_filled :
		return sudoku
	else :
		return [[]]

# This recursive function picks a random digit in the "tab_possible list"
# If it does not contradicts the rules, it goes deeper into the sudoku to fill it
# Else it does contradict the rules, we ask if the tab_possible list is empty
# 	If it is not we remove the digit tried and we start again
# 	Else it returns false
#
# To enable the backtracking, when the function goes deeper we stock the result
# If the result is False, then remove the digit inserted before we went deeper and try toinsert another value
# Else if the return is false and the list empty, we return False
def insert_values_in_sudoku(gs:Gophersat, coord_list:List, sudoku:List[List]) -> bool :

	if not coord_list : # If there is no coord to fill, we have finished
		return True

	tab_possible = [1, 2, 3, 4, 5, 6, 7, 8, 9]

	coord = coord_list.pop(0) # we pick the coord to fill
	i = coord[0]
	j = coord[1]

	while tab_possible : # While the list has digit to test
		
		idx = random.randrange(0, len(tab_possible)) # getting the random number from the list of possible digit not tested
		number_to_insert = tab_possible.pop(idx)

		if is_number_possible(gs, number_to_insert, i, j) :
			sudoku[i][j] = number_to_insert
			insert_success = insert_values_in_sudoku(gs, coord_list, sudoku)

			if insert_success : 
				return True

	return False # If there no more number to test, it means that we got stuck and we backtrack by returning False

def is_number_possible(gs:Gophersat, number_to_insert:int, i:int, j:int) :
	gs.push_pretty_clause([f"{number_to_insert}_{i}_{j}"])
	solvable = gs.solve()

	if not solvable : 
		gs.pop_clause()

	return solvable

def generate_unique_sudoku(difficulty:int, sudoku:List, gs:Gophersat) :

	cpt = 0
	already_visited = []
	hidden_sudoku = sudoku.copy()

	while cpt < 15 :
		
		i = random.randrange(0, 9) # On chope des coordonnées au hasard
		j = random.randrange(0, 9)

		if (i, j) not in already_visited :
			
			gs.remove_pretty_clause([f"{sudoku[i][j]}_{i}_{j}"])
			gs.solve()

			hidden_sudoku[i][j] = ' '
			already_visited.append((i, j))
			cpt += 1

	if not is_there_one_model(gs) :
		print(f"Error : more than one model : {gs.count_model()}")
	else :
		return hidden_sudoku

def is_there_one_model(gs:Gophersat) :
	return gs.count_model() == 1

if __name__ == "__main__" : 

	voc = generate_voca()

	gs = Gophersat(gophersat_exec, voc)

	insert_rules(gs, voc)

	sudoku = generate_random_sudoku(gs)
	for row in sudoku :
		print(row)

	gs.solve()
	gs.count_model()

	print("=================")

	hidden_sudoku = generate_unique_sudoku(0, sudoku, gs)
	for row in hidden_sudoku :
		print(row)
