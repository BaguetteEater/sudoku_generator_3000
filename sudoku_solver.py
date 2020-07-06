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

		print(case)

		ib = 3*(i//3) # coordinates of the forst case of the square
		jb = 3*(j//3)

		ou_clause = [case]
		for i_prime in range(ib, ib+3) :
			for j_prime in range(jb, jb+3) :
				if i != i_prime or j != j_prime :
					print(i_prime, j_prime)
					ou_clause.append(f"{num_case}_{i_prime}_{j_prime}")	
					gs.push_pretty_clause([f"-{case}", f"-{num_case}_{i_prime}_{j_prime}"])

		gs.push_pretty_clause(ou_clause)
		ou_clause = []

def insert_rules(gs, voc) :
	insert_only_one_number_in_case(gs, voc)
	insert_one_value_in_row(gs, voc)
	insert_one_value_in_col(gs, voc)
	insert_one_value_in_square(gs, voc)

def generate_random_sudoku(gs) :

	sudoku = [[0 for x in range(9)] for y in range(9)]

	for i in range(9) :
		 

if __name__ == "__main__" : 

	voc = generate_voca()

	gs = Gophersat(gophersat_exec, voc)

	insert_rules(gs, voc)

	gs.push_pretty_clause(["1_0_0"])
	gs.push_pretty_clause(["2_0_1"])
	print(gs.solve())
	print(gs.get_pretty_model())
