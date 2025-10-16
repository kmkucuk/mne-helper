
import glob
import importlib
import os
import os.path as op
import sys
from optparse import OptionParser


def main():
    cmd = sys.argv[1]
    cmd = importlib.import_module(f".pyeeg_{cmd}")
    print('your command: ', cmd)

if __name__ == "__main__":
    main()