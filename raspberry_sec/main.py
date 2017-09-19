import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from raspberry_sec.system import PCASystem

def main():
    print('Starting up service')
    pca_system = PCASystem()
    pca_system.run()

if __name__ == '__main__':
    main()