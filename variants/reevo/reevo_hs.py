import subprocess
import numpy as np
import json
import tiktoken
from utils.utils import *


class ReEvoHS:
    def __init__(self, cfg, root_dir) -> None:
        self.cfg = cfg
        self.root_dir = root_dir

        self.mutation_rate = cfg.mutation_rate
        self.iteration = 0
        self.function_evals = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.elitist = None
        self.best_obj_overall = float("inf")
        self.long_term_reflection_str = ""
        self.best_obj_overall = None
        self.best_code_overall = None
        self.best_code_path_overall = None

        self.init_prompt()
        self.init_population()

    def init_prompt(self) -> None:
        self.problem = self.cfg.problem.problem_name
        self.problem_desc = self.cfg.problem.description
        self.problem_size = self.cfg.problem.problem_size
        self.func_name = self.cfg.problem.func_name
        self.obj_type = self.cfg.problem.obj_type
        self.problem_type = self.cfg.problem.problem_type

        logging.info("Problem: " + self.problem)
        logging.info("Problem description: " + self.problem_desc)
        logging.info("Function name: " + self.func_name)

        self.prompt_dir = f"{self.root_dir}/baselines/reevo/prompts"
        self.output_file = f"{self.root_dir}/problems/{self.problem}/gpt.py"

        # Loading all text prompts
        # Problem-specific prompt components
        prompt_path_suffix = "_black_box" if self.problem_type == "black_box" else ""
        problem_prompt_path = f'{self.prompt_dir}/{self.problem}{prompt_path_suffix}'
        self.seed_func = file_to_string(f'{problem_prompt_path}/seed_func.txt')
        self.func_signature = file_to_string(f'{problem_prompt_path}/func_signature.txt')
        self.func_desc = file_to_string(f'{problem_prompt_path}/func_desc.txt')
        if os.path.exists(f'{problem_prompt_path}/external_knowledge.txt'):
            self.external_knowledge = file_to_string(f'{problem_prompt_path}/external_knowledge.txt')
            self.long_term_reflection_str = self.external_knowledge
        else:
            self.external_knowledge = ""

        # Common prompts
        self.system_generator_prompt = file_to_string(f'{self.prompt_dir}/common/system_generator.txt')
        self.system_reflector_prompt = file_to_string(f'{self.prompt_dir}/common/system_reflector.txt')
        self.user_reflector_st_prompt = file_to_string(
            f'{self.prompt_dir}/common/user_reflector_st.txt') if self.problem_type != "black_box" else file_to_string(
            f'{self.prompt_dir}/common/user_reflector_st_black_box.txt')  # shrot-term reflection
        self.user_reflector_lt_prompt = file_to_string(
            f'{self.prompt_dir}/common/user_reflector_lt.txt')  # long-term reflection
        self.crossover_prompt = file_to_string(f'{self.prompt_dir}/common/crossover.txt')
        self.mutataion_prompt = file_to_string(f'{self.prompt_dir}/common/mutation.txt')
        self.user_generator_prompt = file_to_string(f'{self.prompt_dir}/common/user_generator.txt').format(
            func_name=self.func_name,
            problem_desc=self.problem_desc,
            func_desc=self.func_desc,
        )
        self.seed_prompt = file_to_string(f'{self.prompt_dir}/common/seed.txt').format(
            seed_func=self.seed_func,
            func_name=self.func_name,
        )

        self.system_hs_prompt = file_to_string(f'{self.prompt_dir}/common/system_harmony_search.txt')
        self.hs_prompt = file_to_string(f'{self.prompt_dir}/common/harmony_search.txt')

        # Flag to print prompts
        self.print_crossover_prompt = True  # Print crossover prompt for the first iteration
        self.print_mutate_prompt = True  # Print mutate prompt for the first iteration
        self.print_short_term_reflection_prompt = True  # Print short-term reflection prompt for the first iteration
        self.print_long_term_reflection_prompt = True  # Print long-term reflection prompt for the first iteration
        self.print_hs_prompt = True
        self.local_sel_hs = None

    def cal_usage_LLM(self, lst_prompt, lst_completion, encoding_name="cl100k_base"):
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        for i in range(len(lst_prompt)):
            for message in lst_prompt[i]:
                for key, value in message.items():
                    self.prompt_tokens += len(encoding.encode(value))

        for i in range(len(lst_completion)):
            self.completion_tokens += len(encoding.encode(lst_completion[i]))


    def init_population(self) -> None:
        # Evaluate the seed function, and set it as Elite
        logging.info("Evaluating seed function...")
        code = extract_code_from_generator(self.seed_func).replace("v1", "v2")
        logging.info("Seed function code: \n" + code)
        seed_ind = {
            "stdout_filepath": f"problem_iter{self.iteration}_stdout0.txt",
            "code_path": f"problem_iter{self.iteration}_code0.py",
            "code": code,
            "response_id": 0,
        }
        self.seed_ind = seed_ind
        self.population = self.evaluate_population([seed_ind])

        # If seed function is invalid, stop
        if not self.seed_ind["exec_success"]:
            raise RuntimeError(f"Seed function is invalid. Please check the stdout file in {os.getcwd()}.")

        self.update_iter()

        # Generate responses
        system = self.system_generator_prompt
        user = self.user_generator_prompt + "\n" + self.seed_prompt + "\n" + self.long_term_reflection_str

        pre_messages = {"system": system, "user": user}
        messages = format_messages(self.cfg, pre_messages)
        logging.info("Initial Population Prompt: \nSystem Prompt: \n" + system + "\nUser Prompt: \n" + user)

        # Write to file
        file_name = f"problem_iter{self.iteration}_prompt.txt"
        with open(file_name, 'w') as file:
            file.writelines(json.dumps(pre_messages))

        responses = multi_chat_completion([messages], self.cfg.init_pop_size, self.cfg.model,
                                          self.cfg.temperature + 0.3)  # Increase the temperature for diverse initial population
        self.cal_usage_LLM([messages], responses)

        population = [self.response_to_individual(response, response_id) for response_id, response in
                      enumerate(responses)]

        # Run code and evaluate population
        population = self.evaluate_population(population)

        # Update iteration
        self.population = population
        self.update_iter()

    def response_to_individual(self, response: str, response_id: int, file_name: str = None) -> dict:
        """
        Convert response to individual
        """
        # Write response to file
        file_name = f"problem_iter{self.iteration}_response{response_id}.txt" if file_name is None else file_name + ".txt"
        with open(file_name, 'w') as file:
            file.writelines(response + '\n')

        code = extract_code_from_generator(response)

        # Extract code and description from response
        std_out_filepath = f"problem_iter{self.iteration}_stdout{response_id}.txt" if file_name is None else file_name + "_stdout.txt"

        individual = {
            "stdout_filepath": std_out_filepath,
            "code_path": f"problem_iter{self.iteration}_code{response_id}.py",
            "code": code,
            "response_id": response_id,
            "tryHS": False,
        }
        return individual

    def mark_invalid_individual(self, individual: dict, traceback_msg: str) -> dict:
        """
        Mark an individual as invalid.
        """
        individual["exec_success"] = False
        individual["obj"] = float("inf")
        individual["traceback_msg"] = traceback_msg
        return individual

    def save_log_population(self, population: list[dict], logHS=False):
        objs = [individual["obj"] for individual in population]

        if logHS is False:
            file_name = f"objs_log_iter{self.iteration}.txt"
            with open(file_name, 'w') as file:
                file.writelines("\n".join(map(str, objs)) + '\n')
        else:
            file_name = f"objs_log_iter{self.iteration}_hs.txt"
            with open(file_name, 'w') as file:
                file.writelines("\n".join(map(str, objs + [self.local_sel_hs])) + '\n')

    def evaluate_population(self, population: list[dict], hs_try_idx: int = None) -> list[dict]:
        """
        Evaluate population by running code in parallel and computing objective values.
        """
        inner_runs = []
        # Run code to evaluate
        for response_id in range(len(population)):
            self.function_evals += 1
            # Skip if response is invalid
            if population[response_id]["code"] is None:
                population[response_id] = self.mark_invalid_individual(population[response_id], "Invalid response!")
                inner_runs.append(None)
                continue

            logging.info(f"Iteration {self.iteration}: Running Code {response_id}")

            try:
                process = self._run_code(population[response_id], response_id)
                inner_runs.append(process)
            except Exception as e:  # If code execution fails
                logging.info(f"Error for response_id {response_id}: {e}")
                population[response_id] = self.mark_invalid_individual(population[response_id], str(e))
                inner_runs.append(None)

        # Update population with objective values
        for response_id, inner_run in enumerate(inner_runs):
            if inner_run is None:  # If code execution fails, skip
                continue
            try:
                inner_run.communicate(timeout=self.cfg.timeout)  # Wait for code execution to finish
            except subprocess.TimeoutExpired as e:
                logging.info(f"Error for response_id {response_id}: {e}")
                population[response_id] = self.mark_invalid_individual(population[response_id], str(e))
                inner_run.kill()
                continue

            individual = population[response_id]
            stdout_filepath = individual["stdout_filepath"]
            with open(stdout_filepath, 'r') as f:  # read the stdout file
                stdout_str = f.read()
            traceback_msg = filter_traceback(stdout_str)

            individual = population[response_id]
            # Store objective value for each individual
            if traceback_msg == '':  # If execution has no error
                try:
                    individual["obj"] = float(stdout_str.split('\n')[-2]) if self.obj_type == "min" else -float(
                        stdout_str.split('\n')[-2])
                    individual["exec_success"] = True
                except:
                    population[response_id] = self.mark_invalid_individual(population[response_id],
                                                                           "Invalid std out / objective value!")
            else:  # Otherwise, also provide execution traceback error feedback
                population[response_id] = self.mark_invalid_individual(population[response_id], traceback_msg)

            if hs_try_idx is None:
                logging.info(
                    f"Iteration {self.iteration}, response_id {response_id}: Objective value: {individual['obj']}")
            else:
                logging.info(f"Iteration {self.iteration}, hs_try {hs_try_idx}: Objective value: {individual['obj']}")

        return population

    def _run_code(self, individual: dict, response_id) -> subprocess.Popen:
        """
        Write code into a file and run eval script.
        """
        logging.debug(f"Iteration {self.iteration}: Processing Code Run {response_id}")

        with open(self.output_file, 'w') as file:
            file.writelines(individual["code"] + '\n')

        # Execute the python file with flags
        with open(individual["stdout_filepath"], 'w') as f:
            eval_file_path = f'{self.root_dir}/problems/{self.problem}/eval.py' if self.problem_type != "black_box" else f'{self.root_dir}/problems/{self.problem}/eval_black_box.py'
            process = subprocess.Popen(['python3', '-u', eval_file_path, f'{self.problem_size}', self.root_dir, "train"],
                                       stdout=f, stderr=f)

        block_until_running(individual["stdout_filepath"], log_status=True, iter_num=self.iteration,
                            response_id=response_id)
        return process

    def update_iter(self) -> None:
        """
        Update after each iteration
        """
        population = self.population
        objs = [individual["obj"] for individual in population]
        best_obj, best_sample_idx = min(objs), np.argmin(np.array(objs))

        # update best overall
        if self.best_obj_overall is None or best_obj < self.best_obj_overall:
            self.best_obj_overall = best_obj
            self.best_code_overall = population[best_sample_idx]["code"]
            self.best_code_path_overall = population[best_sample_idx]["code_path"]

        # update elitist
        if self.elitist is None or best_obj < self.elitist["obj"]:
            self.elitist = population[best_sample_idx]
            logging.info(f"Iteration {self.iteration}: Elitist: {self.elitist['obj']}")

        logging.info(f"Iteration {self.iteration} finished...")
        logging.info(f"Best obj: {self.best_obj_overall}, Best Code Path: {self.best_code_path_overall}")
        logging.info(f"LLM usage: prompt_tokens = {self.prompt_tokens}, completion_tokens = {self.completion_tokens}")
        logging.info(f"Function Evals: {self.function_evals}")
        self.iteration += 1

    def random_select(self, population: list[dict]) -> list[dict]:
        """
        Random selection, select individuals with equal probability.
        """
        selected_population = []
        # Eliminate invalid individuals
        if self.problem_type == "black_box":
            population = [individual for individual in population if
                          individual["exec_success"] and individual["obj"] < self.seed_ind["obj"]]
        else:
            population = [individual for individual in population if individual["exec_success"]]
        if len(population) < 2:
            return None
        trial = 0
        while len(selected_population) < 2 * self.cfg.pop_size:
            trial += 1
            parents = np.random.choice(population, size=2, replace=False)
            # If two parents have the same objective value, consider them as identical; otherwise, add them to the selected population
            if parents[0]["obj"] != parents[1]["obj"]:
                selected_population.extend(parents)
            if trial > 1000:
                return None
        return selected_population

    def gen_short_term_reflection_prompt(self, ind1: dict, ind2: dict) -> tuple[list[dict], str, str]:
        """
        Short-term reflection before crossovering two individuals.
        """
        if ind1["obj"] == ind2["obj"]:
            print(ind1["code"], ind2["code"])
            raise ValueError("Two individuals to crossover have the same objective value!")
        # Determine which individual is better or worse
        if ind1["obj"] < ind2["obj"]:
            better_ind, worse_ind = ind1, ind2
        elif ind1["obj"] > ind2["obj"]:
            better_ind, worse_ind = ind2, ind1

        worse_code = filter_code(worse_ind["code"])
        better_code = filter_code(better_ind["code"])

        system = self.system_reflector_prompt
        user = self.user_reflector_st_prompt.format(
            func_name=self.func_name,
            func_desc=self.func_desc,
            problem_desc=self.problem_desc,
            worse_code=worse_code,
            better_code=better_code
        )

        pre_messages = {"system": system, "user": user}
        message = format_messages(self.cfg, pre_messages)

        # Print reflection prompt for the first iteration
        if self.print_short_term_reflection_prompt:
            logging.info("Short-term Reflection Prompt: \nSystem Prompt: \n" + system + "\nUser Prompt: \n" + user)
            self.print_short_term_reflection_prompt = False
        return message, worse_code, better_code

    def short_term_reflection(self, population: list[dict]) -> tuple[list[list[dict]], list[str], list[str]]:
        """
        Short-term reflection before crossovering two individuals.
        """
        messages_lst = []
        worse_code_lst = []
        better_code_lst = []
        for i in range(0, len(population), 2):
            # Select two individuals
            parent_1 = population[i]
            parent_2 = population[i + 1]

            # Short-term reflection
            messages, worse_code, better_code = self.gen_short_term_reflection_prompt(parent_1, parent_2)
            messages_lst.append(messages)
            worse_code_lst.append(worse_code)
            better_code_lst.append(better_code)

        # Asynchronously generate responses
        response_lst = multi_chat_completion(messages_lst, 1, self.cfg.model, self.cfg.temperature)
        self.cal_usage_LLM(messages_lst, response_lst)
        return response_lst, worse_code_lst, better_code_lst

    def long_term_reflection(self, short_term_reflections: list[str]) -> None:
        """
        Long-term reflection before mutation.
        """
        system = self.system_reflector_prompt
        user = self.user_reflector_lt_prompt.format(
            problem_desc=self.problem_desc,
            prior_reflection=self.long_term_reflection_str,
            new_reflection="\n".join(short_term_reflections),
        )

        pre_messages = {"system": system, "user": user}
        messages = format_messages(self.cfg, pre_messages)

        if self.print_long_term_reflection_prompt:
            logging.info("Long-term Reflection Prompt: \nSystem Prompt: \n" + system + "\nUser Prompt: \n" + user)
            self.print_long_term_reflection_prompt = False

        self.long_term_reflection_str = multi_chat_completion([messages], 1, self.cfg.model, self.cfg.temperature)[0]
        self.cal_usage_LLM([messages], [self.long_term_reflection_str])

        # Write reflections to file
        file_name = f"problem_iter{self.iteration}_short_term_reflections.txt"
        with open(file_name, 'w') as file:
            file.writelines("\n".join(short_term_reflections) + '\n')

        file_name = f"problem_iter{self.iteration}_long_term_reflection.txt"
        with open(file_name, 'w') as file:
            file.writelines(self.long_term_reflection_str + '\n')

    def crossover(self, short_term_reflection_tuple: tuple[list[list[dict]], list[str], list[str]]) -> list[dict]:
        reflection_content_lst, worse_code_lst, better_code_lst = short_term_reflection_tuple
        messages_lst = []
        num_choice = 0
        for reflection, worse_code, better_code in zip(reflection_content_lst, worse_code_lst, better_code_lst):
            # Crossover
            system = self.system_generator_prompt
            func_signature0 = self.func_signature.format(version=0)
            func_signature1 = self.func_signature.format(version=1)
            user = self.crossover_prompt.format(
                user_generator=self.user_generator_prompt,
                func_signature0=func_signature0,
                func_signature1=func_signature1,
                worse_code=worse_code,
                better_code=better_code,
                reflection=reflection,
                func_name=self.func_name,
            )

            pre_messages = {"system": system, "user": user}
            messages = format_messages(self.cfg, pre_messages)
            messages_lst.append(messages)

            # Write to file
            file_name = f"problem_iter{self.iteration}_response{num_choice}_prompt.txt"
            with open(file_name, 'w') as file:
                file.writelines(json.dumps(pre_messages))
            num_choice += 1

            # Print crossover prompt for the first iteration
            if self.print_crossover_prompt:
                logging.info("Crossover Prompt: \nSystem Prompt: \n" + system + "\nUser Prompt: \n" + user)
                self.print_crossover_prompt = False

        # Asynchronously generate responses
        response_lst = multi_chat_completion(messages_lst, 1, self.cfg.model, self.cfg.temperature)
        self.cal_usage_LLM(messages_lst, response_lst)
        crossed_population = [self.response_to_individual(response, response_id) for response_id, response in
                              enumerate(response_lst)]

        assert len(crossed_population) == self.cfg.pop_size
        return crossed_population

    def mutate(self) -> list[dict]:
        """Elitist-based mutation. We only mutate the best individual to generate n_pop new individuals."""
        system = self.system_generator_prompt
        func_signature1 = self.func_signature.format(version=1)
        user = self.mutataion_prompt.format(
            user_generator=self.user_generator_prompt,
            reflection=self.long_term_reflection_str + self.external_knowledge,
            func_signature1=func_signature1,
            elitist_code=filter_code(self.elitist["code"]),
            func_name=self.func_name,
        )

        pre_messages = {"system": system, "user": user}
        messages = format_messages(self.cfg, pre_messages)

        # Write to file
        file_name = f"problem_iter{self.iteration}_prompt.txt"
        with open(file_name, 'w') as file:
            file.writelines(json.dumps(pre_messages))

        if self.print_mutate_prompt:
            logging.info("Mutation Prompt: \nSystem Prompt: \n" + system + "\nUser Prompt: \n" + user)
            self.print_mutate_prompt = False
        responses = multi_chat_completion([messages], int(self.cfg.pop_size * self.mutation_rate), self.cfg.model,
                                          self.cfg.temperature)
        self.cal_usage_LLM([messages], responses)
        population = [self.response_to_individual(response, response_id) for response_id, response in
                      enumerate(responses)]
        return population

    def sel_individual_hs(self):
        candidate_hs = [individual for individual in self.population if individual["tryHS"] is False]
        best_candidate_id = self.find_best_obj(candidate_hs)
        self.local_sel_hs = best_candidate_id
        self.population[best_candidate_id]['tryHS'] = True
        return self.population[best_candidate_id]['code']

    def initialize_harmony_memory(self, bounds):
        problem_size = len(bounds)
        harmony_memory = np.zeros((self.cfg.hm_size, problem_size))
        for i in range(problem_size):
            lower_bound, upper_bound = bounds[i]
            harmony_memory[:, i] = np.random.uniform(lower_bound, upper_bound, self.cfg.hm_size)
        return harmony_memory

    def responses_to_population(self, responses, try_hs_idx=None) -> list[dict]:
        """
        Convert responses to population. Applied to the initial population.
        """
        population = []
        for response_id, response in enumerate(responses):
            filename = None if try_hs_idx is None else f"problem_iter{self.iteration}_hs{try_hs_idx}"
            individual = self.response_to_individual(response, response_id, filename)
            population.append(individual)
        return population

    def create_population_hs(self, str_code, parameter_ranges, harmony_memory, try_hs_idx=None):
        str_create_pop = []
        for i in range(len(harmony_memory)):
            tmp_str = str_code
            for j in range(len(list(parameter_ranges))):
                tmp_str = tmp_str.replace(('{' + list(parameter_ranges)[j] + '}'), str(harmony_memory[i][j]))
                if tmp_str == str_code:
                    return None
            str_create_pop.append(tmp_str)

        population_hs = self.responses_to_population(str_create_pop, try_hs_idx)
        return self.evaluate_population(population_hs, try_hs_idx)

    def find_best_obj(self, population_hs):
        objs = [individual["obj"] for individual in population_hs]
        best_solution_id = np.argmin(np.array(objs))
        return best_solution_id

    def create_new_harmony(self, harmony_memory, bounds):
        new_harmony = np.zeros((harmony_memory.shape[1],))
        for i in range(harmony_memory.shape[1]):
            if np.random.rand() < self.cfg.hmcr:
                new_harmony[i] = harmony_memory[np.random.randint(0, harmony_memory.shape[0]), i]
                if np.random.rand() < self.cfg.par:
                    adjustment = np.random.uniform(-1, 1) * (bounds[i][1] - bounds[i][0]) * self.cfg.bandwidth
                    new_harmony[i] += adjustment
            else:
                new_harmony[i] = np.random.uniform(bounds[i][0], bounds[i][1])
        return new_harmony

    def update_harmony_memory(self, population_hs, harmony_memory, new_harmony, func_block, parameter_ranges,
                              try_hs_idx):
        objs = [individual["obj"] for individual in population_hs]
        worst_index = np.argmax(np.array(objs))

        new_individual = self.create_population_hs(func_block, parameter_ranges, [new_harmony.tolist()], try_hs_idx)[0]

        if new_individual['obj'] < population_hs[worst_index]['obj']:
            population_hs[worst_index] = new_individual
            harmony_memory[worst_index] = new_harmony
        return population_hs, harmony_memory

    def harmony_search(self):
        system = self.system_hs_prompt
        user = self.hs_prompt.format(code_extract=self.sel_individual_hs())
        pre_messages = {"system": system, "user": user}
        messages = format_messages(self.cfg, pre_messages)
        # Print get hs prompt for the first iteration
        if self.print_hs_prompt:
            logging.info("Harmony Search Prompt: \nSystem Prompt: \n" + system + "\nUser Prompt: \n" + user)
            self.print_hs_prompt = False

        # Write to file
        file_name = f"problem_iter{self.iteration}_prompt.txt"
        with open(file_name, 'w') as file:
            file.writelines(json.dumps(pre_messages))

        responses = multi_chat_completion([messages], 1, self.cfg.model, self.cfg.temperature)
        self.cal_usage_LLM([messages], [str(responses[0])])

        logging.info("LLM Response for HS step: " + str(responses[0]))
        parameter_ranges, func_block = extract_to_hs(responses[0])
        if parameter_ranges is None or func_block is None:
            return None
        bounds = [value for value in parameter_ranges.values()]

        harmony_memory = self.initialize_harmony_memory(bounds)
        population_hs = self.create_population_hs(func_block, parameter_ranges, harmony_memory)

        if population_hs is None:
            return None
        elif len([individual for individual in population_hs if individual["exec_success"] is True]) == 0:
            self.function_evals -= self.cfg.hm_size
            return None

        for iteration in range(self.cfg.max_iter):
            new_harmony = self.create_new_harmony(harmony_memory, bounds)
            population_hs, harmony_memory = self.update_harmony_memory(population_hs, harmony_memory, new_harmony,
                                                                       func_block, parameter_ranges, iteration)
        best_obj_id = self.find_best_obj(population_hs)
        population_hs[best_obj_id]["tryHS"] = True
        return population_hs[best_obj_id]

    def evolve(self):
        while self.function_evals < self.cfg.max_fe:
            # If all individuals are invalid, stop
            if all([not individual["exec_success"] for individual in self.population]):
                raise RuntimeError(f"All individuals are invalid. Please check the stdout files in {os.getcwd()}.")
            # Select
            population_to_select = self.population if (self.elitist is None or self.elitist in self.population) else [
                                                                                                                         self.elitist] + self.population  # add elitist to population for selection
            selected_population = self.random_select(population_to_select)
            if selected_population is None:
                raise RuntimeError("Selection failed. Please check the population.")
            # Short-term reflection
            short_term_reflection_tuple = self.short_term_reflection(
                selected_population)  # (response_lst, worse_code_lst, better_code_lst)
            # Crossover
            crossed_population = self.crossover(short_term_reflection_tuple)
            # Evaluate
            self.population = self.evaluate_population(crossed_population)
            # Update
            self.update_iter()
            # Long-term reflection
            self.long_term_reflection([response for response in short_term_reflection_tuple[0]])
            # Mutate
            mutated_population = self.mutate()
            # Evaluate
            self.population.extend(self.evaluate_population(mutated_population))
            # Update
            self.update_iter()

            self.save_log_population(self.population, False)

            # Harmony Search
            try_hs_num = 3
            while try_hs_num:
                individual_hs = self.harmony_search()
                if individual_hs is not None:
                    self.population.extend([individual_hs])
                    # self.update_iter()
                    self.save_log_population([individual_hs], True)
                    break
                else:
                    try_hs_num -= 1
            self.update_iter()
        return self.best_code_overall, self.best_code_path_overall
