import sys,os
sys.path.append(os.getcwd())
 
from distributed_worker.loader import load
from distributed_worker.api import run

if __name__ == "__main__":
    load()
    run()