import os
import sys
import subprocess
import uuid
import tempfile

from typing import List, Dict

__author__ = "Sylvain Lagrue"
__copyright__ = "Copyright 2019, 2020 UTC"
__license__ = "LGPL-3.0"
__version__ = "0.4.1"
__maintainer__ = "Ulysse Brehon"
__email__ = "ulysse.brehon@gmail.com"
__status__ = "dev"

USAGE = f"""usage: python {os.sys.argv[0]} cnf_file"""

"""
ADDED IN 0.4.1
-> count_model()
Thanks to the API of the Gophersat exec, we use the '-count' option to count the number of pssible models
Can take a while, use with caution

-> remove_clause(self, clause)
Allow the user to remove a specific clause in their gophersat format

-> remove_pretty_clause(self, pretty_clause)
Allow the user to pop a specific clause from the clause base in the pretty format

TODO :
- vérif qu'on n'a pas ajouté une variable de plus au moment d'ajouter les clauses
- vérif que la liste de voc est de taille suffisante...
- gérer directement une bib dynamique...
"""


class Gophersat:
    def __init__(
        self, gophersat_exec: str = "gophersat", voc: List[str] = [], cnf_file: str = ""
    ):
        # self.find_exec()
        self.__executable = gophersat_exec

        self.__nb_model = 0
        self.__voc = voc
        self.__has_changed = False
        self.__satisfiable = True
        self.__model: List[int] = []
        self.__clauses: List[List[int]] = []
        self.__clause_num = 0
        self.__var_num = 0
        self.__voc_dict: Dict[str, int] = {}

        if cnf_file != "":
            self.read_cnf_file(cnf_file)

        if len(voc) != 0:
            self.voc2dictionnary()

    def changed(self):
        self.__nb_model = 0
        self.__has_changed = True
        self.__satisfiable = None
        self.__model = []

    def voc2dictionnary(self):
        i = 0
        d = {}
        for v in self.__voc:
            d[v] = i
            i += 1

        self.__var_num = len(self.__voc)
        self.__voc_dict = d

    def push_pretty_clause(self, clause: List[str]):
        l = []
        for lit in clause:
            if lit[0] == "-" or lit[0] == "¬":
                l.append(-(self.__voc_dict[lit[1:]] + 1))
            else:
                l.append((self.__voc_dict[lit] + 1))

        self.push_clause(l)

    def push_clause(self, clause: List[int]):
        self.__clauses.append(clause)
        self.__clause_num += 1
        self.changed()

    def pop_clause(self):
        self.__clauses = self.__clauses[:-1]
        self.changed()

    def remove_clause(self, clause):
        self.__clauses.remove(clause)
        self.changed()

    def remove_pretty_clause(self, pretty_clause: List[str]):
        l = []

        for lit in pretty_clause:
            if lit[0] == "-" or lit[0] == "¬":
                l.append(-(self.__voc_dict[lit[1:]] + 1))
            else:
                l.append((self.__voc_dict[lit] + 1))

        self.remove_clause(l)

    def solve(self):
        if not (self.__has_changed):
            return self.__satisfiable

        temporary_dir = tempfile.gettempdir()
        temporary_file_name = f"{os.path.join(temporary_dir, uuid.uuid4().hex)}.cnf"

        with open(temporary_file_name, "w", newline="\n") as f:
            f.write(self.dimacs())

        res = subprocess.run(
            [self.__executable, f.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        os.remove(temporary_file_name)

        err = res.stderr.decode("utf8")
        if err != "":
            print("error:", err)
            sys.exit(2)

        out = res.stdout.decode("utf8")
        lines = out.splitlines()

        sat = lines[1][2:]

        if sat == "SATISFIABLE":
            self.__model = list(map(int, lines[2][2:].split(" ")))[:-1]
            self.__satisfiable = True
        else:
            self.__model = []
            self.__satisfiable = False

        return self.__satisfiable

    def count_model(self):
        if not (self.__has_changed):
            return self.__satisfiable

        temporary_dir = tempfile.gettempdir()
        temporary_file_name = f"{os.path.join(temporary_dir, uuid.uuid4().hex)}.cnf"

        with open(temporary_file_name, "w", newline="\n") as f:
            f.write(self.dimacs())

        res = subprocess.run(
            [self.__executable, "-count",  f.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        os.remove(temporary_file_name)

        err = res.stderr.decode("utf8")
        if err != "":
            print("error:", err)
            sys.exit(2)

        out = res.stdout.decode("utf8")
        lines = out.splitlines()

        self.__nb_model = int(lines[1])

        return self.__nb_model

    def get_model(self):
        return self.__model

    def get_pretty_model(self):
        s = ""
        for i in self.__model:
            if i < 0:
                s += "¬"
            s += f"{self.__voc[abs(i)-1]} ∧ "

        s = s.rstrip("∧ ")

        return s

    def read_cnf_file(self, filename: str):
        self.__var_num = 0
        self.__clause_num = 0
        self.__clauses = []
        self.__has_changed = True

        with open(filename) as f:
            for line in f.readlines():
                l = line.rstrip("\n")
                if len(l) == 0:
                    continue
                elif l[0] == "c":
                    continue
                elif l[0] == "p":
                    continue
                else:
                    self.__clauses.append(self.read_clause(l))
                    self.__clause_num += 1

    def read_clause(self, s: str) -> List[int]:
        l = list(map(int, s.split(" ")))[:-1]
        m = max(l)
        if m > self.__var_num:
            self.__var_num = m

        return l

    def dimacs(self) -> str:
        s = "c automatically generated by gopherpysat\n"
        s += f"p cnf {self.__var_num} {self.__clause_num}\n"

        for clause in self.__clauses:
            for lit in clause:
                s += f"{lit} "
            s += "0\n"

        return s

    def pretty_clause(self, clause):
        s = ""
        for lit in clause:
            if lit < 0:
                s += "¬"
            s += f"{self.__voc[abs(lit)-1]} ∨ "

        s = s.rstrip("∨ ")

        return s

    def __str__(self):
        if self.__voc == []:
            return self.dimacs()

        s = ""
        for clause in self.__clauses:
            s += self.pretty_clause(clause)
            s += "\n"

        return s


def run(filename):
    gs = Gophersat(cnf_file=filename)

    if gs.solve():
        print("SAT", end=": ")
        print(gs.get_model())
    else:
        print("UNSAT")


if __name__ == "__main__":
    if len(os.sys.argv) != 2:
        print(USAGE)
        sys.exit(1)

    cnf = os.sys.argv[1]
    run(cnf)
