import numpy as np
import pandas as pd
from anytree import AnyNode, RenderTree
import sys
import time
import getopt

# Dynamic Programming, forward chain approach to the Container Loading Problem. Since all our costs are 1 or 2, we have
# split this problem into cases of whether there exists a cost of 1 or not.

# railcarFile preprocessing in pandas
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

# stackFile preprocessing in pandas
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

# For a given container, get its most recent depth data from Z
# Input: cont string - containerID, Z DataFrame - Current containers in the stacks
# Output: depth int
def depth(cont, Z):
    depth = Z['contDepth'].loc[Z['contID'] == cont]
    return int(depth)

# For a current set of containers in Y, we want to know the container height of platformID
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
# Ouput: platformIndex int
def platformIndex(cont, R):
    platformIndex = R['platfSequIndex'].loc[R['contID'] == cont]
    platformIndex = platformIndex.iloc[0]
    return platformIndex

# Whether a container choice is valid given current railcar set Y and target R
# Input: cont string - contID, Y DataFrame - set of containers in railcar, R DataFrame - the target config of all conts
# Output: boolean of whether cont is valid
def valid(cont, Y, R):
    if top(cont, R) == height(Y, platformIndex(cont, R)):
        return 1
    else:
        return 0

# The ending state of Z and Y after movement of container from Z (stacks) to Y (railcar)
# Input: cont string - containerID, Z DataFrame - set of containers in Stacks, Y DataFrame - set of containers in railcars,
#       R DataFrame - target configuration of all containers
def move(cont, Z, Y, R):
    # We introduce the stack index '-1' to mean 'ground'
    Z_stack = Z['contStackIndex'].loc[Z['contID'] == cont].iloc[0]
    cont_depth = Z['contDepth'].loc[Z['contID'] == cont].iloc[0]

    for idx, c in Z[Z['contStackIndex'] == Z_stack].iterrows():
        if Z_stack != -1 and cont_depth == 0 and c['contID'] != cont and c['contDepth'] > cont_depth:
            Z.loc[idx, 'contDepth'] = np.where(Z.loc[idx, 'contDepth'] == 1, 0, 1)
        elif c['contDepth'] == 0 and cont_depth == 1 and c['contID'] != cont:
            Z.loc[idx, 'contStackIndex'] = -1
        elif c['contDepth'] == 2 and cont_depth == 1 and c['contID'] != cont:
            Z.loc[idx, 'contDepth'] = 0

    Z = Z[Z['contID'] != cont]
    Y_row = R[R['contID'] == cont]
    Y = Y.append(Y_row, ignore_index=True)
    return Z, Y

# Determine the containers that can be moved from Z to Y satisfying conditions of Depth and Y placement
# Input Z DataFrame - the set of containers in the stack, Y DataFrame - the set of containers on the railcar, R DataFrame - the target configuration of the railcar
# Output: validSet Series of strings - Set of container IDs of valid containers to move
def validContainers(Z, Y, R):
    # Calculate the set difference Z = R \ Y
    validList = []

    for idx, row in Z.iterrows():
        container = row['contID']
        if top(container, R) == height(Y, platformIndex(container, R)) and depth(container, Z) < 2:
            validList.append(container)

    return validList



# Input: stackFile string, railcarFile string
def main(stacksFile, railcarFile):
    # Read in 'Stacks" and "Railcar" files
    stacks_df = stacksPreprocessing(stacksFile)
    railcar_df = railcarPreprocessing(railcarFile)

    # We move one cart per step k, so k is also the number of carts moved
    # N is the total number of carts
    N = railcar_df.shape[0]
    # Initialize Y as having the railcar column names with no data. i.e. The railcar is empty
    # Initialize Z as having the stacks column names with all data. i.e. The stacks are full
    Y = railcar_df.drop(railcar_df.index[0:])
    Z = stacks_df

    # Begin two trees to store the different paths and costs
    rootNode = AnyNode(id='root', cost=0, set=set(), Z=Z, Y=Y)

    for k in range(N):
        print('\n\n --------------------------------- Stage k=' + str(k) + ' ---------------------------------')
        leaves = rootNode.leaves
        for leaf in leaves:
            single=False
            Z = leaf.Z
            Y = leaf.Y

            validChoices = validContainers(Z, Y, railcar_df)
            validNodes = [0]*len(validChoices)
            print(leaf.id)
            print("Valid choice: " + str(validChoices))

            # v is a containerID - string
            for v, i in zip(validChoices, range(len(validChoices))):
                node_set = set(leaf.set)
                node_set.add(v)
                validNodes[i] = AnyNode(id=v, parent=leaf, cost = depth(v, Z)+1, set=node_set)
        # Since we only have two possible costs 1 and 2, we reduce the DP problem to Cases
            # CASE 1: There exists at least 1 cost that is 1 - u_k becomes that container
                # There is also only a single output node
                # from v, take the containerID and move there.
                # Move that containerID row from Z to Y.
            if len(leaves) == 1:
                for u_k in leaf.children:
                    if u_k.cost == 1:
                        leaf.children = [u_k]
                        Z_u, Y_u = move(u_k.id, Z, Y, railcar_df)
                        u_k.Z = Z_u
                        u_k.Y = Y_u
                        single=True
                        break
                if single:
                    break
                else:
                    # Case 2: All options have a cost of 2 with 1 output node
                        # No containers have cost 1
                    for u_k in leaf.children:
                        Z_u, Y_u = move(u_k.id, Z, Y, railcar_df)
                        u_k.Z = Z_u
                        u_k.Y = Y_u
        # Case 3: There is more than one output node
        if len(leaves) > 1:
            for pre, fill, node in RenderTree(rootNode):
                print("%s%s, %s, set=%s" % (pre, node.id, node.cost, node.set))
            for u_k in rootNode.leaves:
                if u_k.cost == 1:
                    Z = u_k.parent.Z
                    Y = u_k.parent.Y
                    leaf = u_k.parent
                    print(u_k.id)
                    print(u_k.parent.id)
                    print(Y['contID'])
                    Z_u, Y_u = move(u_k.id, Z, Y, railcar_df)
                    u_k.Z = Z_u
                    u_k.Y = Y_u
                    # Cut all branches except this one
                    leaf.children = [u_k]
                    fork = u_k
                    child = u_k
                    while True:
                        if len(fork.children) > 1:
                            fork.children = [child]
                            single = True
                            break
                        else:
                            child = fork
                            fork = fork.parent
                    if single:
                        break

            # Case 4: > 1 output nodes and no leaf has cost == 1
                # No containers have cost 1
            if not single:
                for u_k in leaf.children:
                    Z = u_k.parent.Z
                    Y = u_k.parent.Y
                    Z_u, Y_u = move(u_k.id, Z, Y, railcar_df)
                    u_k.Z = Z_u
                    u_k.Y = Y_u

        for pre, fill, node in RenderTree(rootNode):
            print("%s%s, %s, set=%s" % (pre, node.id, node.cost, node.set))

    final_move = rootNode.leaves[0]

    if final_move.Y.shape[0] == N:
        print('All containers have been placed\n')
        print('The containers in order are as follows.\n')
        costs = [np.inf]*(N+1)
        k = 0
        print('containerID \t cost')
        for pre, fill, node in RenderTree(rootNode):

            if node.id != 'root':
                print('%s \t %s' %(node.id, node.cost))
            costs[k] = node.cost
            k += 1
        sumC = sum(costs)
        print('Optimal cost: ' + str(sumC))


    else:
        sys.exit('An error occured with the algorithm.')

def usage():
    print(" -h Help \n-s stack file path \n-r railcar file path")

if __name__ == '__main__':
    # Start timer
    start = time.time()
    stacksFile=""
    railcarFile=""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:r:")
    except getopt.GetoptError as err:
        usage()
        sys.exit('The command line inputs were not given properly')
    for opt, arg in opts:
        if opt == '-s':
            stacksFile = arg
        elif opt == '-r':
            railcarFile = arg
        else:
            usage()
            sys.exit(2)
    if not stacksFile or not railcarFile:
        usage()
        sys.exit(2)

    main(stacksFile, railcarFile)
    print("\n------------------------------------------------")
    print("Time taken to complete in seconds:")
    print(time.time() - start)