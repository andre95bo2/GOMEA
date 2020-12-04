# The problem in the C code is at the function at line 932
# void initializeNewGOMEAMemory() sometimes it finishes sometimes it throws an exception

import population as pop
import numpy as np
import math


# we want the probability than integer i before integer j

def createDependencyMatrix(population):
    # create the matrix
    dependencyMatrix = np.zeros((len(population[0]), len(population[0])))

    nBids = len(population[0])
    for i in range(0, nBids):
        for j in range(i + 1, nBids):
            p = 0
            for k in range(0, len(population)):
                if population[k][i] < population[k][j]:
                    p += 1
            p /= len(population)
            # is this condition true ? yes : no
            # (p==0)||(p==1)?0:-(p*log2(p) + (1.0-p)*log2(1.0-p));
            if p == 0 or p == 1:
                print("this case")
                entropy = 0
            else:
                entropy = -(p*(math.log(p, 2)) + (1.0-p)*(math.log((1.0-p), 2)))
            dependencyMatrix[i][j] = 1 - entropy
            # now we multiply by the inverted average distance between variables (delta2)
            averageDistance = 0
            for k in range(0, len(population)):
                averageDistance += (population[k][i] - population[k][j]) * (population[k][i] - population[k][j])
            averageDistance /= len(population)
            dependencyMatrix[i][j] *= 1 - averageDistance

            # creating the symmetric matrix
            dependencyMatrix[j][i] = dependencyMatrix[i][j]

    return dependencyMatrix


# get the dependency between two clusters based on the matrix
def clustersDependencies(list1, list2, matrix):
    cont = 0
    sum = 0
    for x in list1:
        for y in list2:
            cont += 1
            sum += matrix[x][y]
    return sum/cont

# return the dependencies for each element/cluster of the branch
def getDependenciesForBranch(dependencyMatrix, branch):
    dependency = []
    for i in range(0, len(branch)):
        dep = 0
        stored = []
        for j in range(0, len(branch)):
            if j != i:
                x = clustersDependencies(branch[i], branch[j], dependencyMatrix)
                if x == dep:
                    stored.append(j)
                if x > dep:
                    dep = x
                    stored = [j]

        dependency.append(stored)
    return dependency

def isInList(elem, list):
    if list == []:
        return False
    else:
        if isinstance(list, int):
            if list == elem:
                return True
            else:
                return False
        else:
            for x in range(0, len(list)):
                if isinstance(list[x], int):
                    if elem == list[x]:
                        return True
                else:
                    for y in range(0, len(list[x])):
                        if elem == list[x][y]:
                            return True
            return False

# translate the dependency from a list of indexes to their actual value
def translateDependency(branch, dependency):
    newDep = []
    for x in range(0, len(dependency)):
        newDep.append(branch[dependency[x][0]])
    return newDep

# based on the branch and the dependecy, it creates the next branch
def createNextBranch(branch, dependency):
    dependency = translateDependency(branch, dependency)
    nextBranch = []
    for x in range(0, len(branch)):
        new = []
        for z in range(0, len(branch[x])):
            if not isInList(branch[x][z], nextBranch):
                toAdd = []
                for y in dependency[x]:
                    if not isInList(y, nextBranch):
                        toAdd.append(y)
                if toAdd != []:
                    for j in branch[x]:
                        new.append(j)
                    if isinstance(toAdd, int):
                        new.append(toAdd)
                    else:
                        for j in toAdd:
                            new.append(j)
                    nextBranch.append(new)
    return nextBranch

# it returns the branch with the single element that were not included in any clusters
# it is needed to calculate the dependencies (since a branch doesn't necessary contains all the variables)
def branchWithUnary(oldbranch, newbranch):
    unaryBranch = newbranch.copy()
    for x in oldbranch:
        for y in x:
            flag = False
            if isInList(y, newbranch):
                flag = True
        if flag == False:
            unaryBranch.append(x)
    return unaryBranch



def getUnivariateAndRoot(population):
    univariate = []
    root = []
    for x in range(0, len(population[0])):
        univariate.append([x])
        root.append(x)


    return univariate, [root]

# check if the univariate is the same of the root, undependently of the order of the element
def rootSameUni(root, univariate):
    univ = univariate.copy()
    univ[0].sort()
    return univ == root

def getLinkageTree(population):
    tree = []
    univariate, root = getUnivariateAndRoot(population)
    unaryBranch = univariate.copy()
    tree.append(unaryBranch)
    while not rootSameUni(root, unaryBranch):

        #print("unary branch ", unaryBranch)
        dependencyMatrix = createDependencyMatrix(population)
        dependencies = getDependenciesForBranch(dependencyMatrix, unaryBranch)
        #print("dependencies ", dependencies)
        nextBranch = createNextBranch(unaryBranch, dependencies)
        tree.append(nextBranch)
        #print("next Branch ", nextBranch)
        unaryBranch = branchWithUnary(unaryBranch, nextBranch)
    #print("fine")
    return tree

#population = pop.population(10, "L4-5-5.txt", 1)
#tree = getLinkageTree(population)
#print(tree)


