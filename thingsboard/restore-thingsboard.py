import os
import subprocess
import glob
path = "/home/anttuov/thingsboard/"
ip = "192.168.51.196"

tables = glob.glob('{}*.csv'.format(path))

for table in tables:
    tablename = table.replace(path, '').replace('.csv', '')
    if tablename == "ts_kv_cf":
        os.system("cqlsh {} -e \"COPY thingsboard.{} FROM '{}';\"".format(ip, tablename, table))
    else:
        os.system("cqlsh {} -e \"COPY thingsboard.{} FROM '{}' WITH CHUNKSIZE = 1;\"".format(ip, tablename, table))
