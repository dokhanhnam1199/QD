import sys
sys.path.append('../../')

from typing import Callable

import numpy as np
import time
from joblib import Parallel, delayed
import os
import json

from gls_tsp.eval_helper import readTSPRandom, readTSPLib
from gls_tsp.eval_helper import gls_run


class Evaluation:
    def __init__(self, instance_path=None) -> None:
        self.time_limit = 100  # maximum 100 seconds for each instance
        self.ite_max = 1000  # maximum number of local searchs in GLS for each instance
        self.perturbation_moves = 1  # movers of each edge in each perturbation
        path = os.path.dirname(os.path.abspath(__file__))
        if instance_path is None:
            self.instance_path = path + '/instance/TSPAEL64.pkl'
        else:
            self.instance_path = path + instance_path
        self.debug_mode = False
        self.coords, self.instances, self.opt_costs = readTSPRandom.read_instance_all(self.instance_path)

    def tour_cost(self, instance, solution, problem_size):
        cost = 0
        for j in range(problem_size - 1):
            cost += np.linalg.norm(instance[int(solution[j])] - instance[int(solution[j + 1])])
        cost += np.linalg.norm(instance[int(solution[-1])] - instance[int(solution[0])])
        return cost

    def generate_neighborhood_matrix(self, instance):
        instance = np.array(instance)
        n = len(instance)
        neighborhood_matrix = np.zeros((n, n), dtype=int)

        for i in range(n):
            distances = np.linalg.norm(instance[i] - instance, axis=1)
            sorted_indices = np.argsort(distances)  # sort indices based on distances
            neighborhood_matrix[i] = sorted_indices

        return neighborhood_matrix

    def evaluateGLS(self, heuristic_func: Callable):
        nins = 64
        inputs = [(x, self.opt_costs[x], self.instances[x], self.coords[x], self.time_limit, self.ite_max,
                   self.perturbation_moves, heuristic_func) for x in range(nins)]

        # ====================== Add Runtime Config by RZ ======================
        # read config file and load n_jobs during runtime
        try:
            current_file_abspath = os.path.abspath(__file__)
            directory_path = os.path.dirname(current_file_abspath)
            config_path = os.path.join(directory_path, 'evaluator_runtime_config.json')
            with open(config_path, 'r') as file:
                config_dict = json.load(file)
            n_jobs = config_dict['n_jobs']
        except:
            n_jobs = 4
        # ======================================================================

        try:
            gaps = Parallel(n_jobs=n_jobs, timeout=self.time_limit * 1.1)(
                delayed(gls_run.solve_instance)(*input) for input in inputs)
        except:
            print("This is bug of program")
            return None

        # if there is None in gaps, return None
        for gap in gaps:
            if gap is None:
                return None

        return np.mean(gaps)

    def evaluate(self, heuristic_func: Callable):
        try:
            fitness = self.evaluateGLS(heuristic_func)
            if fitness <= 0:
                fitness = None
            return fitness
        except Exception as e:
            return None


if __name__ == "__main__":
    import ael_alg

    eva = Evaluation()
    eva.evaluate(ael_alg.update_edge_distance)
