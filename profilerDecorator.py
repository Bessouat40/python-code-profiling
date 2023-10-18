import cProfile, pstats, io
from pstats import SortKey

def profiler(func) :
    def profiledFunction(*args, **kwargs) :
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby).strip_dirs()
        ps.dump_stats('./profilingResults.txt')
        return result
    # analyseResults()
    return profiledFunction()


# def analyseResults() :
