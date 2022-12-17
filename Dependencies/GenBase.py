from pymoo.core.callback import Callback
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import ElementwiseDuplicateElimination
from pymoo.termination.default import DefaultMultiObjectiveTermination
from pymoo.core.mutation import Mutation
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from pymoo.util.normalization import denormalize
from pymoo.core.sampling import Sampling
from numpy import np
from datetime import datetime
from random import randint
import random
from pymoo.algorithms.soo.nonconvex.ga import GA
from copy import deepcopy

class ProblemSingleObjective(Problem):
    """
    The CodART single-objective optimization work with only one objective, testability:
    """

    def __init__(self,
                 n_objectives=1,
                 n_refactorings_lowerbound=10,
                 n_refactorings_upperbound=50,
                 evaluate_in_parallel=False,
                 mode='single'  # 'multi'
                 ):
        """
        Args:
            n_objectives (int): Number of objectives
            n_refactorings_lowerbound (int): The lower bound of the refactoring sequences
            n_refactorings_upperbound (int): The upper bound of the refactoring sequences
            mode (str): 'single' or 'multi'
        """

        super(ProblemSingleObjective, self).__init__(n_var=1, n_obj=1, n_constr=0)
        self.n_refactorings_lowerbound = n_refactorings_lowerbound
        self.n_refactorings_upperbound = n_refactorings_upperbound
        self.evaluate_in_parallel = evaluate_in_parallel
        self.mode = mode
        self.n_obj_virtual = n_objectives

    def _evaluate(self,
                  x,  #
                  out,
                  *args,
                  **kwargs):
        """
        This method iterate over a population, execute the refactoring operations in each individual sequentially,
        and compute quality attributes for the refactored version of the program, as objectives of the search
        Args:
            x (Population): x is a matrix where each row is an individual, and each column a variable.\
                We have one variable of type list (Individual) ==> x.shape = (len(Population), 1)
        """

        objective_values = []
        for k, individual_ in enumerate(x):
            # Stage 0: Git restore
            logger.debug("Executing git restore.")
            git_restore(config.PROJECT_PATH)
            logger.debug("Updating understand database after git restore.")
            update_understand_database(config.UDB_PATH)

            # Stage 1: Execute all refactoring operations in the sequence x
            logger.debug(f"Reached Individual with Size {len(individual_[0])}")
            for refactoring_operation in individual_[0]:
                refactoring_operation.do_refactoring()
                # Update Understand DB
                logger.debug(f"Updating understand database after {refactoring_operation.name}.")
                update_understand_database(config.UDB_PATH)

            # Stage 2:
            if self.mode == 'single':
                # Stage 2 (Single objective mode): Considering only one quality attribute, e.g., testability
                score = testability_main(config.UDB_PATH, initial_value=config.CURRENT_METRICS.get("TEST", 1.0))
            else:
                # Stage 2 (Multi-objective mode): Considering one objective based on average of 8 objective
                arr = Array('d', range(self.n_obj_virtual))
                if self.evaluate_in_parallel:
                    # Stage 2 (Multi-objective mode, parallel): Computing quality attributes
                    p1 = Process(target=calc_qmood_objectives, args=(arr,))
                    if self.n_obj_virtual == 8:
                        p2 = Process(target=calc_testability_objective, args=(config.UDB_PATH, arr,))
                        p3 = Process(target=calc_modularity_objective, args=(config.UDB_PATH, arr,))
                        p1.start(), p2.start(), p3.start()
                        p1.join(), p2.join(), p3.join()
                    else:
                        p1.start()
                        p1.join()
                    score = sum([i for i in arr]) / self.n_obj_virtual
                else:
                    # Stage 2 (Multi-objective mode, sequential): Computing quality attributes
                    qmood_quality_attributes = DesignQualityAttributes(udb_path=config.UDB_PATH)
                    o1 = qmood_quality_attributes.average_sum
                    if self.n_obj_virtual == 8:
                        o2 = testability_main(config.UDB_PATH, initial_value=config.CURRENT_METRICS.get("TEST", 1.0))
                        o3 = modularity_main(config.UDB_PATH, initial_value=config.CURRENT_METRICS.get("MODULE", 1.0))
                    else:
                        o2 = 0
                        o3 = 0
                    del qmood_quality_attributes
                    score = (o1 * 6. + o2 + o3) / self.n_obj_virtual

            # Stage 3: Marshal objectives into vector
            objective_values.append([-1 * score])
            logger.info(f"Objective values for individual {k} in mode {self.mode}: {[-1 * score]}")

        # Stage 4: Marshal all objectives into out dictionary
        out['F'] = np.array(objective_values, dtype=float)

def is_equal_2_refactorings_list(a, b):
    """
    This method implement is_equal method which should return True if two instances of Individual class are equal.
    Otherwise, it returns False.
    The duplicate instances are removed from population at each generation.
    Only one instance is held to speed up the search algorithm
    """

    if len(a.X[0]) != len(b.X[0]):
        return False
    for i, ro in enumerate(a.X[0]):
        if ro.name != b.X[0][i].name:
            return False
        if ro.params != b.X[0][i].params:
            return False
    return True

class IntegerMutation(Mutation):
    """
        Select an individual to mutate with mutation probability.
        Only flip one refactoring operation in the selected individual.
    """

    def __init__(self, prob=0.01, initializer: list = None):
        """
        Args:
            prob (float): mutation probability
        """

        super().__init__()
        self.mutation_probability = prob
        self._initializer = initializer

    def _do(self, problem, X, **kwargs):
        for i, individual in enumerate(X):
            r = np.random.random()
            # with a probability of `mutation_probability` replace the refactoring operation with new one
            if r < self.mutation_probability:
                # j is a random index in individual
                j = random.randint(0, len(individual[0]) - 1)
                random_chromosome = random.choice(self._initializer)
                item = random.choice(random_chromosome)
                X[i][0][j] = deepcopy(item)

        return X

class SinglePointCrossover(Crossover):

    def __init__(self, prob=0.9):

        # Define the crossover: number of parents, number of offsprings, and cross-over probability
        super().__init__(n_parents=2, n_offsprings=2, prob=prob)

    def _do(self, problem, X, **kwargs):

        # The input of has the following shape (n_parents, n_matings, n_var)
        _, n_matings, n_var = X.shape

        # The output will be with the shape (n_offsprings, n_matings, n_var)
        # Because there the number of parents and offsprings are equal it keeps the shape of X
        Y = np.full_like(X, None, dtype=object)


        # for each mating provided
        for k in range(n_matings):
            # get the first and the second parent (a and b are instance of individuals)
            a, b = X[0, k, 0], X[1, k, 0]

            len_min = min(len(a), len(b))
            cross_point_1 = random.randint(1, int(len_min * 0.30))
            cross_point_2 = random.randint(int(len_min * 0.70), len_min - 1)
            if random.random() < 0.5:
                cross_point_final = cross_point_1
            else:
                cross_point_final = cross_point_2

            offspring_a = []
            offspring_b = []
            for i in range(0, cross_point_final):
                offspring_a.append(deepcopy(a[i]))
                offspring_b.append(deepcopy(b[i]))

            for i in range(cross_point_final, len_min):
                offspring_a.append(deepcopy(b[i]))
                offspring_b.append(deepcopy(a[i]))

            if len(b) > len(a):
                for i in range(len(a), len(b)):
                    offspring_a.append(deepcopy(b[i]))
            else:
                for i in range(len(b), len(a)):
                    offspring_b.append(deepcopy(a[i]))

            Y[0, k, 0], Y[1, k, 0] = offspring_a, offspring_b

        return Y

class FloatRandomSampling(Sampling):
    def random_by_bounds(self, n_var, xl, xu, n_samples=1):
        val = np.random.random((n_samples, n_var))
        return denormalize(val, xl, xu)
    def random(self, problem, n_samples=1):
        return self.random_by_bounds(problem.n_var, problem.xl, problem.xu, n_samples=n_samples)
    def _do(self, problem, n_samples, **kwargs):
        return self.random(problem, n_samples=n_samples)
class IntegerRandomSampling(FloatRandomSampling):
    def _do(self, problem, n_samples, **kwargs):
        X = super()._do(problem, n_samples, **kwargs)
        return np.around(X).astype(int)
class GenBase:
    """
    MODE = 1
    RANDOM POPULATION
    ==================================
    MODE = 2
    CUSTOM
    """

    RANDOM_MODE = 1

    def __init__(
        self,
        mod: int = 1,
        pop_size: int = 100,
        ge_fitness_evaluations: int = 10000,
        crossover_operator: str = "SP",
        crossover_probability: float = 0.9,
        mutation_operator: str = "INT",
        mutation: float = 0.01,
        pruning: float = 0.01,
        duplication_probabilities: float = 0.01,
        selection_operator: str = "BT",
        maximum_gene_size: int = 20,
        **kwargs
    ):
        self.mode = mod
        if self.mode == 1:
            self.pop_size = pop_size
            self.population = [randint(0, 500) for i in range(0, self.pop_size)]
            self.ge_fitness_evaluations = ge_fitness_evaluations
            self.crossover_operator = crossover_operator
            self.mutation_operator = mutation_operator
            self.mutation = mutation
            self.pruning = pruning
            self.duplication_probabilities = duplication_probabilities
            self.selection_operator = selection_operator
            self.maximum_gene_size = maximum_gene_size
            self.crossover_probability = crossover_probability

    def run(self):
        if self.mode == 1:
           ga = GA(
                pop_size=self.pop_size,
                sampling=IntegerRandomSampling,
                crossover=SinglePointCrossover(prob=self.crossover_probability),
                mutation=IntegerMutation(prob=self.mutation, initializer=self.population),
                eliminate_duplicates=ElementwiseDuplicateElimination(cmp_func=is_equal_2_refactorings_list),
                n_gen=self.maximum_gene_size,

            )

            my_termination = DefaultMultiObjectiveTermination(
                x_tol=None,
                cv_tol=None,
                f_tol=0.0015,
                nth_gen=5,
                n_last=5,
                n_max_gen=1000,  # about 1000 - 1400
                n_max_evals=1e6
            )

            # Do optimization for various problems with various algorithms
            res = minimize(
                problem=ProblemSingleObjective(),
                algorithm=ga,
                termination=my_termination,
                seed=1,
                verbose=False,
                copy_algorithm=True,
                copy_termination=True,
                save_history=False,
            )

            print(f"***** Algorithm was finished in {res.algorithm.n_gen + 20} generations *****")
            print(" ")
            print("============ time information ============")
            print(f"Start time: {datetime.fromtimestamp(res.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"End time: {datetime.fromtimestamp(res.end_time).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Execution time in seconds: {res.exec_time}")
            print(f"Execution time in minutes: {res.exec_time / 60}")
            print(f"Execution time in hours: {res.exec_time / (60 * 60)}")


