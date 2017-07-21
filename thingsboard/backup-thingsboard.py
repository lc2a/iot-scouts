import os
import subprocess
path = "/home/anttuov/thingsboard/"
ip = "192.168.51.140"

describe = subprocess.getoutput("cqlsh {} -e \"use thingsboard; describe tables;\"".format(ip))
tables = []
for tablename in describe.replace("\n", " ").split(" "):
    if tablename.strip() != "":
        tables.append(tablename.strip())

print(tables)
cmd = "".format('')
for table in tables:
    if table != "event":
        os.system("cqlsh {0} -e \"COPY thingsboard.{1} TO '{2}{1}.csv';\"".format(ip, table, path))
