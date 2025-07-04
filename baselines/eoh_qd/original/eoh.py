import numpy as np
import json
import random
import time

from .eoh_interface_EC import InterfaceEC
# main class for eoh
class EOH:

    # initilization
    def __init__(self, paras, problem, select, manage, cfg, **kwargs):
        self.cfg = cfg
        self.prob = problem
        self.select = select
        self.manage = manage
        
        # LLM settings
        self.use_local_llm = paras.llm_use_local
        self.url = paras.llm_local_url
        self.api_endpoint = paras.llm_api_endpoint  # currently only API2D + GPT
        self.api_key = paras.llm_api_key
        self.llm_model = paras.llm_model

        # ------------------ RZ: use local LLM ------------------
        self.use_local_llm = kwargs.get('use_local_llm', False)
        assert isinstance(self.use_local_llm, bool)
        if self.use_local_llm:
            assert 'url' in kwargs, 'The keyword "url" should be provided when use_local_llm is True.'
            assert isinstance(kwargs.get('url'), str)
            self.url = kwargs.get('url')
        # -------------------------------------------------------

        # Experimental settings       
        self.pop_size = paras.ec_pop_size  # popopulation size, i.e., the number of algorithms in population
        self.n_pop = paras.ec_n_pop  # number of populations

        self.operators = paras.ec_operators
        self.operator_weights = paras.ec_operator_weights
        if paras.ec_m > self.pop_size or paras.ec_m == 1:
            print("m should not be larger than pop size or smaller than 2, adjust it to m=2")
            paras.ec_m = 2
        self.m = paras.ec_m

        self.debug_mode = paras.exp_debug_mode  # if debug
        self.ndelay = 1  # default

        self.use_seed = paras.exp_use_seed
        self.seed_path = paras.exp_seed_path
        self.load_pop = paras.exp_use_continue
        self.load_pop_path = paras.exp_continue_path
        self.load_pop_id = paras.exp_continue_id

        self.output_path = paras.exp_output_path

        self.exp_n_proc = paras.exp_n_proc
        
        self.timeout = paras.eva_timeout

        self.use_numba = paras.eva_numba_decorator

        print("- EoH parameters loaded -")

        # Set a random seed
        random.seed(2024)

    # add new individuals to population
    # def add2pop(self, population, offspring):
    #     for off in offspring:
    #         for ind in population:
    #             if ind['objective'] == off['objective']:
    #                 if (self.debug_mode):
    #                     print("duplicated result, retrying ... ")
    #         population.append(off)

    def remove_duplicate(self, population: list[dict]) -> None:
        bd_to_best_individual = {}

        for individual in population:
            try:
                bd_values = tuple(
                    (individual.get(self.cfg.bd_list[i]) or 0) // div
                    for i, div in enumerate(self.cfg.bd_step)
                )
                obj = individual['objective']  # Replace 'objective' with your actual objective key

                if (bd_values not in bd_to_best_individual or obj < bd_to_best_individual[bd_values]['objective']):
                    bd_to_best_individual[bd_values] = individual
            except KeyError as e:
                missing_key = str(e)
                print(f"Skipping individual due to missing behavior descriptor: {missing_key}")
                continue

        population = list(bd_to_best_individual.values())
    
    def add2pop(self, population, evaluated_population):
        # Create a dictionary to map bd values to individuals in population
        bd_to_individual = {
            tuple(
                (individual.get(self.cfg.bd_list[i], 0) or 0) // div
                for i, div in enumerate(self.cfg.bd_step)
            ): individual
            for individual in population
        }

        for evaluated_individual in evaluated_population:
            try:
                # Get the behavior descriptor (bd) values as a tuple
                bd_values = tuple(
                    (evaluated_individual.get(self.cfg.bd_list[i], 0) or 0) // div
                    for i, div in enumerate(self.cfg.bd_step)
                )

                if bd_values in bd_to_individual:
                    # Compare objective values and keep the one with the lower obj value
                    existing_individual = bd_to_individual[bd_values]
                    if evaluated_individual["objective"] < existing_individual["objective"]:
                        bd_to_individual[bd_values] = evaluated_individual
                else:
                    # Add the new individual if no matching bd values exist
                    bd_to_individual[bd_values] = evaluated_individual

            except KeyError as e:
                # Log a warning and skip the individual if a key is missing
                missing_key = str(e)
                print(f"Warning: Missing key {missing_key} in evaluated individual. Skipping this individual.")
                continue

        population = list(bd_to_individual.values())
    

    # run eoh 
    def run(self):

        print("- Evolution ready for", self.prob.problem, "-")

        time_start = time.time()

        # interface for large language model (llm)
        # interface_llm = PromptLLMs(self.api_endpoint,self.api_key,self.llm_model,self.debug_mode)

        # interface for evaluation
        interface_prob = self.prob

        # interface for ec operators
        interface_ec = InterfaceEC(self.pop_size, self.m, self.api_endpoint, self.api_key, self.llm_model,
                                   self.debug_mode, interface_prob, use_local_llm=self.use_local_llm, url=self.url, select=self.select,n_p=self.exp_n_proc,
                                   timeout = self.timeout, use_numba=self.use_numba
                                   )

        # initialization
        population = []
        if self.use_seed:
            with open(self.seed_path) as file:
                data = json.load(file)
            population = interface_ec.population_generation_seed(data)
            filename = self.output_path + "population_generation_0.json"
            with open(filename, 'w') as f:
                json.dump(population, f, indent=5)
            n_start = 0
        else:
            if self.load_pop:  # load population from files
                print("load initial population from " + self.load_pop_path)
                with open(self.load_pop_path) as file:
                    data = json.load(file)
                for individual in data:
                    population.append(individual)
                print("initial population has been loaded!")
                n_start = self.load_pop_id
            else:  # create new population
                print("creating initial population:")
                population = interface_ec.population_generation()
                self.remove_duplicate(population)
                population = self.manage.population_management(population, self.pop_size)

                # print(len(population))
                # if len(population)<self.pop_size:
                #     for op in [self.operators[0],self.operators[2]]:
                #         _,new_ind = interface_ec.get_algorithm(population, op)
                #         self.add2pop(population, new_ind)
                #         population = self.manage.population_management(population, self.pop_size)
                #         if len(population) >= self.pop_size:
                #             break
                #         print(len(population))
     
                
                print(f"Pop initial: ")
                for off in population:
                    print(" Obj: ", off['objective'], end="|")
                print()
                print("initial population has been created!")
                # Save population to a file
                filename = self.output_path + "population_generation_0.json"
                with open(filename, 'w') as f:
                    json.dump(population, f, indent=5)
                n_start = 0

        # main loop
        n_op = len(self.operators)

        for pop in range(n_start, self.n_pop):  
            #print(f" [{na + 1} / {self.pop_size}] ", end="|")         
            for i in range(n_op):
                op = self.operators[i]
                print(f" OP: {op}, [{i + 1} / {n_op}] ", end="|") 
                op_w = self.operator_weights[i]
                if (np.random.rand() < op_w):
                    parents, offsprings = interface_ec.get_algorithm(population, op)
                self.add2pop(population, offsprings)  # Check duplication, and add the new offspring
                for off in offsprings:
                    print(" Obj: ", off['objective'], end="|")
                # if is_add:
                #     data = {}
                #     for i in range(len(parents)):
                #         data[f"parent{i + 1}"] = parents[i]
                #     data["offspring"] = offspring
                #     with open(self.output_path + "/results/history/pop_" + str(pop + 1) + "_" + str(
                #             na) + "_" + op + ".json", "w") as file:
                #         json.dump(data, file, indent=5)
                # populatin management
                size_act = min(len(population), self.pop_size)
                population = self.manage.population_management(population, size_act)
                print()


            # Save population to a file
            filename = self.output_path + "population_generation_" + str(pop + 1) + ".json"
            with open(filename, 'w') as f:
                json.dump(population, f, indent=5)

            # Save the best one to a file
            filename = self.output_path + "best_population_generation_" + str(pop + 1) + ".json"
            with open(filename, 'w') as f:
                json.dump(population[0], f, indent=5)


            print(f"--- {pop + 1} of {self.n_pop} populations finished. Time Cost:  {((time.time()-time_start)/60):.1f} m")
            print("Pop Objs: ", end=" ")
            for i in range(len(population)):
                print(str(population[i]['objective']) + " ", end="")
            print()
        
        return population[0]["code"], filename


