import os
import time
import importlib
from typing import Callable

import numpy as np
import sys

sys.path.append('../../')
from baselines.eoh.gls_tsp_adapt.tsp_eval_helper import utils
from baselines.eoh.gls_tsp_adapt.tsp_eval_helper import gls_evol


def solve_instance(n, opt_cost, dis_matrix, coord, time_limit, ite_max, perturbation_moves, heuristic_func: Callable):
    # time_limit = 60 # maximum 10 seconds for each instance
    # ite_max = 1000 # maximum number of local searchs in GLS for each instance
    # perturbation_moves = 1 # movers of each edge in each perturbation

    # time.sleep(1)
    t = time.time()
    # algorithm_module = importlib.import_module("ael_alg")
    # algorithm = importlib.reload(algorithm_module)

    # RZ: simply get the pointer of the heuristic function
    algorithm = heuristic_func

    try:
        init_tour = gls_evol.nearest_neighbor_2End(dis_matrix, 0).astype(int)
        init_cost = utils.tour_cost_2End(dis_matrix, init_tour)
        nb = 100
        nearest_indices = np.argsort(dis_matrix, axis=1)[:, 1:nb + 1].astype(int)

        best_tour, best_cost, iter_i = gls_evol.guided_local_search(coord, dis_matrix, nearest_indices, init_tour,
                                                                    init_cost,
                                                                    t + time_limit, ite_max, perturbation_moves,
                                                                    first_improvement=False, guide_algorithm=algorithm)

        gap = (best_cost / opt_cost - 1) * 100

    except Exception as e:
        # print("Error:", str(e))  # Print the error message
        gap = None

    # print(f"instance {n + 1}: cost = {best_cost:.3f}, gap = {gap:.3f}, n_it = {iter_i}, cost_t = {time.time() - t:.3f}")

    return gap


def solve_instance_tsplib(n, name, scale, dis_matrix, coord, time_limit, ite_max, perturbation_moves,
                          heuristic: Callable, temp_file_path):
    t = time.time()

    try:
        init_tour = gls_evol.nearest_neighbor_2End(dis_matrix, 0).astype(int)
        init_cost = utils.tour_cost_2End(dis_matrix, init_tour)
        nb = 100
        nearest_indices = np.argsort(dis_matrix, axis=1)[:, 1:nb + 1].astype(int)

        best_tour, best_cost, iter_i = gls_evol.guided_local_search(coord, dis_matrix, nearest_indices, init_tour,
                                                                    init_cost,
                                                                    t + time_limit, ite_max, perturbation_moves,
                                                                    first_improvement=False, guide_algorithm=heuristic)
        # path = os.path.dirname(os.path.abspath(__file__))
        # path = os.path.join(path, '.tsp_lib_res.txt')
        path = temp_file_path
        with open(path, 'a') as f:
            f.write(f"File,{name},")
            f.write(f"Best_Cost,{best_cost * scale},")
            f.write(f"Time_Cost,{time.time() - t}\n")

    except Exception as e:
        # print("Error:", str(e))  # Print the error message
        gap = 1E10

    # print(f"instance {name}: cost = {best_cost * scale:.3f}, n_it = {iter_i}, cost_t = {time.time() - t:.3f}")

    return best_cost * scale
