import os
import sys

directory = os.getcwd().split('/')
directory = directory[:-1]
directory = '/'.join(directory)

sys.path.append(directory)