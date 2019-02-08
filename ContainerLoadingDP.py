import numpy as np
import pandas as pd
from anytree import AnyNode, RenderTree
import sys

# Input railcarFile string
# Output railcar_df DataFrame
def railcarPreprocessing(railcarFile):
    railcar_df = pd.read_csv(railcarFile, sep='\t', lineterminator='\r').dropna(axis=0, how='any')
    for column in railcar_df:
        if railcar_df[column].dtype == 'float64':
            railcar_df[column] = railcar_df[column].astype(int)
    railcar_df["platfSequIndex"] = railcar_df["platfSequIndex"].astype(int)
    railcar_df['contInit'] = railcar_df['contInit'].str.strip('\n')
    railcar_df['contID'] = railcar_df['contInit'] + '_' + railcar_df['contNumb'].map(str)
    railcar_df['carID'] = railcar_df['carInit'] + '_' + railcar_df['carNumb'].map(str)
    railcar_df['carSlotBin'] = np.where(railcar_df['carSlotLevel'] == 'top', 1, 0)

    railcar_df = railcar_df.drop(['contInit', 'contNumb', 'carInit', 'carNumb', 'carSlotLevel'], axis=1)
    return railcar_df

# Input stacksFile string
# Output stacks_df DataFrame
def stacksPreprocessing(stacksFile):
    stacks_df = pd.read_csv(stacksFile, sep='\t', lineterminator='\r').dropna(axis=0, how='any')
    for column in stacks_df:
        if stacks_df[column].dtype == 'float64':
            stacks_df[column] = stacks_df[column].astype(int)
    stacks_df['contInit'] = stacks_df['contInit'].str.strip('\n')
    stacks_df['contID'] = stacks_df['contInit'] + '_' + stacks_df['contNumb'].map(str)
    stacks_df = stacks_df.drop(['contInit', 'contNumb'], axis=1)

    return stacks_df

# For a given container, get it's most recent depth data from Z
# Input: cont string - containerID, Z DataFrame - Current containers in the stacks
# Output: depth int
def depth(cont, Z):
    depth = Z['contDepth'].loc[Z['contID'] == cont]
    return int(depth)

# For a current set of containers, we want to know the container height of platformID
# Input: Y DataFrame - the set of containers on the railcar, platformID int - the platform on the railcar
# Output: height int
def height(Y, platformID):
    platform = Y.loc[Y['platfSequIndex'] == platformID]
    height = platform.shape[0]
    return height

# For container cont, return 1 if it is a top container in R, 0 otherwise
# Input: cont string - unique container ID, R DataFrame - target configuration
# Output: Int in {0,1}
def top(cont, R):
    top = R['carSlotBin'].loc[R['contID'] == cont]
    top = top.iloc[0]
    return top

# Find the platform in R where cont resides
# Input: cont string - the contID, R DataFrame - the set of all containers in their proper position on the railcars.
def platformIndex(cont, R):
    platformIndex = R['platfSequIndex'].loc[R['contID'] == cont]
    platformIndex = platformIndex.iloc[0]
    return platformIndex

def valid(cont, Y, R):
    if top(cont, R) == height(Y, platformIndex(cont, R)):
        return 1
    else:
        return 0

# Input Z DataFrame - the set of containers in the stack, Y DataFrame - the set of containers on the railcar, R DataFrame - the target configuration of the railcar
# Output: validSet Series of strings - Set of container IDs of valid containers to move
def validContainers(Z, Y, R):
    # Calculate the set difference Z = R \ Y
    Y_set = set([tuple(line) for line in Y.values])
    R_set = set([tuple(line) for line in R.values])
    print(Z.columns)
    validList = []

    for idx, row in Z.iterrows():
        container = row['contID']
        if top(container, R) == height(Y, platformIndex(container, R)) and depth(container, Z) < 2:
            validList.append(container)

    return validList



# Input: stackFile string, railcarFile string
def main(argv):
    # Read in 'Stacks" and "Railcar" files
    # TODO Add Getopt later
    stacks_df = stacksPreprocessing(argv[0])
    railcar_df = railcarPreprocessing(argv[1])

    # We move one cart per step k, so k is also the number of carts moved
    # N is the total number of carts
    N = railcar_df.shape[0]
    # Initialize Y as having the railcar column names with no data. i.e. The railcar is empty
    # Initialize Z as having the stacks column names with all data. i.e. The stacks are full
    Y = railcar_df.drop(railcar_df.index[0:])
    Z = stacks_df

    # Begin two trees to store the different paths and costs
    rootNode = AnyNode(id='root', cost=0)
   # rootCost = Node(0)

    for k in range(1):
        validChoices = validContainers(Z, Y, railcar_df)
        validNodes = [0]*len(validChoices)
        validCosts = [3]*len(validChoices)
        print(validNodes)
        # v is a containerID - string
        for v, i in zip(validChoices, range(len(validChoices))):
            validNodes[i] = AnyNode(id=v, parent=rootNode, cost = depth(v,Z)+1)
            #validCosts[i] = Node(depth(v,Z)+1, parent=rootCost)
            # get Depth and put in the tree as well
            # does anytree have a concept of 'arc cost'?
            # Choose the arc with a minimum cost
            # Similar to Dijkstra's, we make a single choice. The min cost of our current options
            # from v, take the containerID and move there.
            # Move that containerID row from Z to Y.
        print(validNodes)
    for pre, fill, node in RenderTree(rootNode):
        print("%s%s, %s" % (pre, node.id, node.cost))



if __name__ == '__main__':
    main(sys.argv[1:])