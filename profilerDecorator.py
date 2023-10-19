import cProfile, pstats, io
from pandas import DataFrame, to_numeric
from pstats import SortKey
from re import split
from matplotlib.pyplot import xticks, savefig

def profiler(**dict) :
    def profiledFunction(func) :
        def wrapper(*params, **dictFunc) :
            pr = cProfile.Profile()
            pr.enable()
            for i in range(dict['nbrIter']) :
                result = func(*params, **dictFunc)
            pr.disable()
            s = io.StringIO()
            sortby = SortKey.CUMULATIVE
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            folder = dict['pngFolder']
            csvPath = dict['pngFolder'] + '/profiling.csv'
            ps.print_stats()
            stats = s.getvalue()
            df = analyseResults(stats)
            saveFigures(df, folder)
            df.drop('filename:lineno(function)', axis=1)
            df.to_csv(csvPath, index=False, sep=";")
            return result
        return wrapper
    return profiledFunction

def saveFigures(df, folder) :
    cumTimes = folder + '/cumTimes.jpg'
    nbrCalls = folder + '/nbrCalls.jpg'
    df.nlargest(5, 'cumtime').plot.bar(x = 'filename:lineno(function)', y = 'cumtime')
    xticks(rotation=-45, ha='left')
    savefig(cumTimes, bbox_inches='tight')
    df.nlargest(5, 'cumtime').plot.bar(x = 'filename:lineno(function)', y = 'ncalls')
    xticks(rotation=-45, ha='left')
    savefig(nbrCalls, bbox_inches='tight')

def analyseResults(stats) :
    resultsLines = list(filter(lambda value : value != "", split(r'ncalls.*?\(function\)\n', stats)[1].split("\n")))
    finalIdx = 5
    columns = ['ncalls', 'tottime', 'percall', 'cumtime', "percall2", 'filename:lineno(function)']
    numericsColumns = ['ncalls', 'tottime', 'percall', 'cumtime', "percall2"]
    df = DataFrame(columns = columns)
    for element in resultsLines :
        line = list(filter(lambda x : x!= "", element.strip().replace('\n', '').split(' ')))
        df.loc[len(df)] = [" ".join(line[finalIdx:])  if i == finalIdx else line[i] for i in range(finalIdx + 1)]
    df['ncalls'] = df['ncalls'].apply(lambda x : x.split('/')[0])
    for numericColumn in numericsColumns :
        df[numericColumn] = to_numeric(df[numericColumn])
    df = splitFilenameLineFunctionColumns(df)
    return df

def splitFilenameLineFunctionColumns(df) :
    columnToChange = df['filename:lineno(function)'].values
    file, line, function = [], [], []
    for value in columnToChange :
        split_value = list(filter(lambda x : x != "", split(r"(.*?):([\d]+)(.*)", value)))
        if len(split_value) == 3 :
            file.append(split_value[0])
            line.append(split_value[1])
            function.append(split_value[2])
        else :
            file.append("")
            line.append("")
            function.append("")
    df['file'] = file
    df['line'] = line
    df['function'] = function
    return df