from reporting import *
import config

files = config.files

df = createDf(files)

graph(df)