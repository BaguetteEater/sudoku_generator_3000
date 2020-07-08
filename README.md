# sudoku_solver.py

## hide_case_sudoku 
`def hide_case_sudoku(difficulty:int, sudoku:List, gs:Gophersat) `

It hides random cases one by one

At each case which has not been hidden already, we check if removing it adds solution to the puzzle

If there is more than one solution at the end, it return a empty grid

Else it returns the hidden sudoku



TODO : 

	- Find a solution with acktracking to avoid returning a empty grid

	- Take in consideration the difficulty parameter



## print_sudoku -> bool 
`def print_sudoku(file_name:str, sudoku:List[List]) -> bool `

Creates a text file containing the given sudoku

Returns False if the operation fail

Returns True if the operation is a success



## generate_sudoku -> Tuple[List, List]
`def generate_sudoku() -> Tuple[List, List]`

Generates th vocabulary and initilize the Gophersat with it

It insert the rules to apply when generating a sudoku

Uses the Gophersat to generates one full sudoku

Then it hides cases with the assurance that there is one and only solution

Returns a Tuple containing the solution and the playable sudoku



## is_number_possible 
`def is_number_possible(gs:Gophersat, number_to_insert:int, i:int, j:int) `

Ask for the possibility for a number to be at the position (i, j)

Returns False if adding the number to the sudoku grid breaks the model and gives a non solvable solution

Returns True otherwise

Calling this function will add a clause to the Gophersat resolver but it is automaticly removed if it breaks the model



## generate_random_sudoku -> List 
`def generate_random_sudoku(gs:Gophersat) -> List `

starting function of recursive backtracking

and return the resolved sudoku



## generate_voca  -> List 
`def generate_voca () -> List `

Generate all the voca needed for the SAT solver

A symbol reprensents the precense (or not) of one number at the given (i, j) position

Format : 1_i_j , 2__i_j , 3_i_j ... 9_i_j with i and j belong to [0..8]



## insert_one_value_in_row 
`def insert_one_value_in_row(gs:Gophersat, voca:List) `

1_i_j <-> non(1_i_0) ET non(1_i_2) ET non(1_i_3) ET ... ET non(1_i_8) 



## is_there_one_model 
`def is_there_one_model(gs:Gophersat) `



## insert_rules 
`def insert_rules(gs, voc) `



## insert_only_one_number_in_case  
`def insert_only_one_number_in_case (gs:Gophersat, voca:List) `

1_i_j <-> non(2_i_j) ET non(3_i_j) ET ... non(9_i_j)

Ce qui devient : 

1_i_j OU 2_i_j OU 3_i_j OU ... OU 9_i_j

ET

non(1_i_j) OU non(2_i_j) ET non(1_i_j) OU non(3_i_j) ET ... ET non(1_i_j) OU non(9_i_j) 



## insert_one_value_in_col 
`def insert_one_value_in_col(gs:Gophersat, voca:List) `

1_i_j <-> non(1_0_j) ET non(1_1_j) ET non(1_2_j) ET ... ET non(1_3_j) 



## insert_one_value_in_square 
`def insert_one_value_in_square(gs:Gophersat, voca:List) `

i^b = 3 x (i//3)

j^b = 3 x (j//3)

1_i_j <-> non(1_ib_jb) ET non(1_ib+1_jb) ET non(1_ib+2_jb) ET ... ET non(1_ib+2_jb+2)



## insert_values_in_sudoku -> bool 
`def insert_values_in_sudoku(gs:Gophersat, coord_list:List, sudoku:List[List]) -> bool `

This recursive function picks a random digit in the "tab_possible list"

If it does not contradicts the rules, it goes deeper into the sudoku to fill it

Else it does contradict the rules, we ask if the tab_possible list is empty

	If it is not we remove the digit tried and we start again

	Else it returns false



To enable the backtracking, when the function goes deeper we stock the result

If the result is False, then remove the digit inserted before we went deeper and try toinsert another value

Else if the return is false and the list empty, we return False



