import numpy as np
import pandas as pd
import sys

# Input railcarFile string
# Output railcar_df DataFrame
def railcarPreprocessing(railcarFile):
    railcar_df = pd.read_csv(railcarFile, sep='\t', lineterminator='\r').dropna(axis=0, how='any')
    railcar_df['contInit'] = railcar_df['contInit'].str.strip('\n')
    railcar_df['contID'] = railcar_df['contInit'] + '_' + railcar_df['contNumb'].map(int).map(str)
    railcar_df['carID'] = railcar_df['carInit'] + '_' + railcar_df['carNumb'].map(int).map(str)
    railcar_df['carSlotBin'] = np.where(railcar_df['carSlotLevel'] == 'top', 1, 0)

    railcar_df = railcar_df.drop(['contInit', 'contNumb', 'carInit', 'carNumb', 'carSlotLevel'], axis=1)
    return railcar_df

# Input stacksFile string
# Output stacks_df DataFrame
def stacksPreprocessing(stacksFile):
    stacks_df = pd.read_csv(stacksFile, sep='\t', lineterminator='\r').dropna(axis=0,                                                                     how='any')  # TODO Add Getopt later
    stacks_df['contInit'] = stacks_df['contInit'].str.strip('\n')
    stacks_df['contID'] = stacks_df['contInit'] + '_' + stacks_df['contNumb'].map(int).map(str)
    stacks_df = stacks_df.drop(['contInit', 'contNumb'], axis=1)

    return stacks_df

# Input: stackFile string, railcarFile string
def main(argv):
    # Read in 'Stacks" and "Railcar" files
    stacksFile = argv[0]
    railcarFile = argv[1]


    railcar_df = railcarPreprocessing(railcarFile)

    print(railcar_df)

# Pre-process Stacks data


    print(stacks_df)




if __name__ == '__main__':
    main(sys.argv[1:])