import time
from enum import IntEnum
import numpy as np


# helper class
class Terminations(IntEnum):
    NO_TERMINATION = 0
    MAX_FUNCTION_EVALUATIONS = 1
    MAX_RUNTIME = 2
    FITNESS_THRESHOLD = 3


class Optimizer(object):
    """Base class of all optimizers for continuous black-box minimization.
    """
    def __init__(self, problem, options):
        # problem-related settings
        self.fitness_function = problem.get('fitness_function')
        self.ndim_problem = problem['ndim_problem']
        self.upper_boundary = problem.get('upper_boundary')
        self.lower_boundary = problem.get('lower_boundary')
        self.initial_upper_boundary = problem.get('initial_upper_boundary', self.upper_boundary)
        self.initial_lower_boundary = problem.get('initial_lower_boundary', self.lower_boundary)
        self.problem_name = problem.get('problem_name')
        if (self.problem_name is None) and hasattr(self.fitness_function, '__name__'):
            self.problem_name = self.fitness_function.__name__

        # optimizer-related options
        self.max_function_evaluations = options.get('max_function_evaluations', np.Inf)
        self.max_runtime = options.get('max_runtime', np.Inf)
        self.fitness_threshold = options.get('fitness_threshold', -np.Inf)
        self.n_individuals = options.get('n_individuals')
        self.seed_rng = options.get('seed_rng')
        if self.seed_rng is None:
            self.rng = np.random.default_rng()
        else:
            self.rng = np.random.default_rng(self.seed_rng)
        self.seed_initialization = options.get('seed_initialization', self.rng.integers(np.iinfo(np.int64).max))
        self.rng_initialization = np.random.default_rng(self.seed_initialization)
        self.seed_optimization = options.get('seed_optimization', self.rng.integers(np.iinfo(np.int64).max))
        self.rng_optimization = np.random.default_rng(self.seed_optimization)
        self.record_options = options.get('record_options')
        self.verbose_options = options.get('verbose_options')

        # auxiliary members
        self.Terminations = Terminations
        self.n_function_evaluations = options.get('n_function_evaluations', 0)
        self.start_function_evaluations = None
        self.time_function_evaluations = options.get('time_function_evaluations', 0)
        self.runtime = options.get('runtime', 0)
        self.start_time = None
        self.best_so_far_y = options.get('best_so_far_y', np.Inf)
        self.best_so_far_x = None
        self.termination_signal = None

    def _check_terminations(self):
        self.runtime = time.time() - self.start_time
        if self.n_function_evaluations >= self.max_function_evaluations:
            termination_signal = True, Terminations.MAX_FUNCTION_EVALUATIONS
        elif self.runtime >= self.max_runtime:
            termination_signal = True, Terminations.MAX_RUNTIME
        elif self.best_so_far_y <= self.fitness_threshold:
            termination_signal = True, Terminations.FITNESS_THRESHOLD
        else:
            termination_signal = False, Terminations.NO_TERMINATION
        return termination_signal

    def _collect_results(self):
        return {'best_so_far_x': self.best_so_far_x,
                'best_so_far_y': self.best_so_far_y,
                'n_function_evaluations': self.n_function_evaluations,
                'runtime': time.time() - self.start_time,
                'termination_signal': self.termination_signal,
                'time_function_evaluations': self.time_function_evaluations}

    def initialize(self):
        raise NotImplementedError

    def iterate(self):
        raise NotImplementedError

    def optimize(self, fitness_function=None):
        raise NotImplementedError
