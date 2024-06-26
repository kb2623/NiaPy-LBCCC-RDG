# encoding=utf8
import os
import sys
import timeit

import numpy as np
from numpy.random import rand

from cec2013lsgo.cec2013 import Benchmark

from niapy.task import Task
from niapy.problems import Problem

from niapy.algorithms.algorithm import (
    AnalysisAlgorithm,
    OptimizationAlgorithm
)
from niapy.algorithms.analysis import (
    RecursiveDifferentialGrouping,
    RecursiveDifferentialGroupingV2,
    RecursiveDifferentialGroupingV3,
    EfficientRecursiveDifferentialGrouping,
    ThreeLevelRecursiveDifferentialGrouping
)
from niapy.algorithms.basic import (
    ParticleSwarmAlgorithm,
    ParticleSwarmOptimization,
    CenterParticleSwarmOptimization,
    MutatedParticleSwarmOptimization,
    MutatedCenterParticleSwarmOptimization,
    ComprehensiveLearningParticleSwarmOptimizer,
    MutatedCenterUnifiedParticleSwarmOptimization,
    OppositionVelocityClampingParticleSwarmOptimization,
)
from ccalgorithm import CooperativeCoevolution


class CEC2013lsgoTask(Task):
    Name:list[str] = ['CEC2013lsgo']
    
    def __init__(self, no_fun:int, *args:list, **kwargs:dict) -> None:
        if 1 < no_fun > 15: raise Exception('Function between 1 and 15!!!')
        bench = Benchmark()
        info = bench.get_info(no_fun)
        max_evals = 3e6
        fun_fitness = bench.get_function(no_fun)
        
        class CEC2013lsgoProblem(Problem):
            def __init__(self, *args:list, **kwargs:dict) -> None:
                kwargs.pop('dimension', None), kwargs.pop('lower', None), kwargs.pop('upper', None)
                super().__init__(dimension=info['dimension'], lower=info['lower'], upper=info['upper'], *args, **kwargs)
        
            def _evaluate(self, x):
                return fun_fitness(x)

        kwargs.pop('problem', None), kwargs.pop('optimization_type', None), kwargs.pop('lower', None), kwargs.pop('upper', None), kwargs.pop('dimension', None), kwargs.pop('max_evals', None)
        super().__init__(problem=CEC2013lsgoProblem(), max_evals=max_evals, *args, **kwargs)

    def get_mesures(self) -> list[float]:
        r = [self.fitness_evals[0][1], self.fitness_evals[0][1], self.fitness_evals[0][1]]
        for e in self.fitness_evals:
            if e[0] > 120000: break
            else: r[0] = e[1]
        for e in self.fitness_evals:
            if e[0] > 600000: break
            else: r[1] = e[1]
        for e in self.fitness_evals:
            if e[0] > 3000000: break
            else: r[2] = e[1]
        return r


def no_seps(a:list) -> int:
    s = 0
    for e in a:
        if len(e) > 1: continue
        s += 1
    return s


def no_groups(a:list) -> int:
    s = 0
    for e in a:
        if len(e) == 1: continue
        s += 1
    return s


def run_rdg_cec2013(no_fun:int = 1, seed:int = 1, alpha:float = 1e-12, NP:int = 50) -> None:
    algo = RecursiveDifferentialGroupingV3(seed=seed)
    algo.set_parameters(n=NP, alpha=alpha)
    task = CEC2013lsgoTask(no_fun=no_fun)
    start = timeit.default_timer()
    best = algo.run(task)
    stop = timeit.default_timer()
    if not os.path.exists('./%s.cec2013lso.%d.csv' % (algo.Name[1], no_fun)):
        with open('%s.cec2013lso.%d.csv' % (algo.Name[1], no_fun), 'w') as csvfile:
            csvfile.write('seed, no_groups, no_seps, evals, time\n')
    with open('%s.cec2013lso.%d.csv' % (algo.Name[1], no_fun), 'a') as csvfile:
        csvfile.write('%d, %d, %d, %d, %f\n' % (seed, no_groups(best), no_seps(best), task.evals, stop - start))


def run_cec2013(opt:type[OptimizationAlgorithm] = ParticleSwarmAlgorithm, no_fun:int = 1, seed:int = 1) -> None:
    algo = opt(seed=seed)
    task = CEC2013lsgoTask(no_fun=no_fun)
    start = timeit.default_timer()
    res = algo.run(task)
    stop = timeit.default_timer()
    if not os.path.exists('%s.%s.%d.csv' % (algo.Name[1], task.Name[0], no_fun)):
        with open('%s.%s.%d.csv' % (algo.Name[1], task.Name[0], no_fun), 'w') as csvfile:
            csvfile.write('seed, f1, f2, f3, time\n')
    with open('%s.%s.%d.csv' % (algo.Name[1], task.Name[0], no_fun), 'a') as csvfile:
        f1, f2, f3 = task.get_mesures()
        csvfile.write('%d, %f, %f, %f, %f\n' % (seed, f1, f2, f3, stop - start))


def run_cc_cec2013(decomp:type[AnalysisAlgorithm] = RecursiveDifferentialGroupingV3, opt:type[OptimizationAlgorithm] = ParticleSwarmAlgorithm, no_fun:int = 1, seed:int = 1) -> None:
    algo = CooperativeCoevolution(decomp(seed=seed), opt, seed=seed)
    task = CEC2013lsgoTask(no_fun=no_fun)
    start = timeit.default_timer()
    res = algo.run(task)
    stop = timeit.default_timer()
    if not os.path.exists('%s.%s.%s.%d.csv' % (algo.decompozer.Name[1], algo.toptimizer.Name[1], task.Name[0], no_fun)):
        with open('%s.%s.%s.%d.csv' % (algo.decompozer.Name[1], algo.toptimizer.Name[1], task.Name[0], no_fun), 'w') as csvfile:
            csvfile.write('seed, f1, f2, f3, time\n')
    with open('%s.%s.%s.%d.csv' % (algo.decompozer.Name[1], algo.toptimizer.Name[1], task.Name[0], no_fun), 'a') as csvfile:
        f1, f2, f3 = task.get_mesures()
        csvfile.write('%d, %f, %f, %f, %f\n' % (seed, f1, f2, f3, stop - start))


if __name__ == "__main__":
    arg_no_fun = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    arg_seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    arg_opt_alg = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    arg_decomp_alg = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    opt_alg = ParticleSwarmAlgorithm
    if arg_opt_alg == 2: opt_alg = ParticleSwarmOptimization
    elif arg_opt_alg == 3: opt_alg = CenterParticleSwarmOptimization
    elif arg_opt_alg == 4: opt_alg = MutatedParticleSwarmOptimization
    elif arg_opt_alg == 5: opt_alg = MutatedCenterParticleSwarmOptimization
    elif arg_opt_alg == 6: opt_alg = OppositionVelocityClampingParticleSwarmOptimization
    elif arg_opt_alg == 7: opt_alg = ComprehensiveLearningParticleSwarmOptimizer
    decomp_alg = RecursiveDifferentialGroupingV3
    if arg_decomp_alg == 1: decomp_alg = RecursiveDifferentialGrouping
    elif arg_decomp_alg == 2: decomp_alg = RecursiveDifferentialGroupingV2
    elif arg_decomp_alg == 3: decomp_alg = RecursiveDifferentialGroupingV3
    elif arg_decomp_alg == 4: decomp_alg = EfficientRecursiveDifferentialGrouping
    elif arg_decomp_alg == 5: decomp_alg = ThreeLevelRecursiveDifferentialGrouping
    if len(sys.argv) == 4: run_cec2013(opt=opt_alg, no_fun=arg_no_fun, seed=arg_seed)
    elif len(sys.argv) >= 5: run_cc_cec2013(decomp=decomp_alg, opt=opt_alg, no_fun=arg_no_fun, seed=arg_seed)

