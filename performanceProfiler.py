import cProfile, pstats, io
from pstats import SortKey

with open("simpleJavaCompiler.py", "r") as f:
    src = f.read()

cProfile.run(src)