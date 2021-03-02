import random
import math
import copy

# read a file containing the adjacency node list of a graph
# Each row contains a vertex of the graph followed by the list of vertices it shares edges with
# return it in list format:
# [[node1, nodes sharing edges with node 1],...,[nodeN, nodes sharing edges with nodeN]]
def RetrieveNodeList():
    f = open('kargerMinCut', 'r')
    flines = f.read().splitlines()
    f.close()
    a = [i.split() for i in flines]
    nodelist = [0] * len(a)
    for i in range(len(a)):
        nodelist[i] = [int(j) for j in a[i]]
    # Uncomment to test with easier graph examples. 1st case min-cut is 2. 2nd case min-cut is 1:
    # nodelist = [[1, 2, 3, 4], [2, 1, 3, 4, 6], [3, 1, 2, 4], [4, 1, 2, 3, 5], [5, 4, 6, 7, 8], [6, 2, 5, 7, 8], [7, 5, 6, 8], [8, 5, 6, 7]]
    # nodelist = [[1, 2, 3, 4, 9], [2, 1, 3, 4, 5, 6, 9], [3, 1, 2, 4, 9], [4, 1, 2, 3, 5, 9], [5, 2, 4, 6, 7, 8, 10], [6, 2, 5, 7, 8, 10], [7, 5, 6, 8, 10, 11], [8, 5, 6, 7, 10], [9, 1, 2, 3, 4], [10, 5, 6, 7, 8], [11, 7]]
    return nodelist

# Transform a Graph node adjacency list into a list of edges
# edgelist =[[edge1], [edge2], [edgeM]
# where [edge] = [X, Y], being X and Y the nodes where edge lies in between
def TransformToEdgeList(nodelist):
    edgelist = []
    for node in nodelist:
        for i in node[1:]:
            # when inspecting node i, add edge if other node (k) is higher than i.
            # If other node k is lower than i, edge will be added when inspecting i = k.
            if i >= node[0]:
                edgelist += [[node[0], i]]
    return edgelist.copy()

# Return a random edge from a list of edges
def RandomChooseEdge (edgelist):
    r = random.randint(0, len(edgelist) - 1)
    return edgelist[r].copy()

# Reduce a list by removing the elements corresponding to the provided indexes
def ReduceList(lista, listofindex):
    for i in reversed(listofindex):
        del lista[i]
    return lista

# Contract pair of nodes from a Graph recursively given a list of edges.
# Keep track of nodes belonging to the same group of merged nodes.
# Contraction works recursively as follows:
# 1. Check if base case is reached: when all nodes but 2, have been removed.
#   1.1 Remove self loops
#   1.2 Return the amount of parallel edges between the 2 remaining edges
# 2. Otherwise recurse by removing edges and merging nodes as follows:
#   2.1 Select uniformly at random and edge to be removed
#   2.2 In case that the selected edge was already "removed" or parallel to it(self loop of
#       merged edge) - update the whole list of edges and remove all the accumulated "removed" and "self loops"
#       up till now.
#      * Note that the edge list is only updated at this point (also when entering in the base case prior to
#      returning the final amount of edges. This is to avoid the cost of evaluating and updating the edge list
#      in every single recursion. Instead, a list tracking nodes belonging to same groups is maintained (and used
#      to update the list of edges, only at this point)
#      ** The list is updated at this point to avoid the "bad luck" of triggering the random edge selection and
#       choosing the removed (or self loop) edge again and again.
#       2.2.1 Do a recursion to choose randomly a new edge (this time it cannot pick a "removed" or self loop
#       edge as they have been already removed.
#   2.3 In case that the random edge is still not removed, update the list which tracks groups of merged nodes:
#       2.3.1 if both vertices still do not belong to a "merged" group, assign them to a new group
#       2.3.2 if one vertex belong to a group, and the other doesnt, assign it to that "merged" group
#       2.3.3 if both vertices belong to different groups, then merge both groups by assigning all vertices
#       from one group to the other.
#       2.3.4 Every time 2.3 is reached we add +1 to the amount of edges removed(merged)
#       2.3.5 Do a recursion to choose randomly a new edge and so on, until the amount of edges removed is
#       all but two. This will trigger the base case, returning the amount of parallel edges in the final cut
def ContractNodes(edgelist):
    # global variable defined in the main function. Needs to remain constant on each recursion
    global NodesToBeRemoved
    # global variables initialised in the main function which updates in each recursion
    global RemovedNodes
    global NodesTrack
    global NewGroup
    # if all nodes but 2 have been removed we are in the base case. Remove all remaining self loops and return
    # the amount of edges among the last 2 standing vertices
    if RemovedNodes == NodesToBeRemoved:
        k = []
        # for each edge check to which group its vertices belong to (at this point only 2 groups remain)
        # if they belong to the same group note its index in the list "k"
        for i in range(len(edgelist)):
            if NodesTrack[edgelist[i][0] - 1] == NodesTrack[edgelist[i][1] - 1]:
                k += [i]
        # remove all edges from the list whose index has been noted in "k"
        reduced = ReduceList(edgelist, k)
        # return the amount of parallel edges among last 2 standing vertices (this will be the possible min cut)
        return len(reduced)
    # if the base case is not reached, keep merging vertices recursively, by selecting a new edge at random
    else:
        # select a new edge
        edge = RandomChooseEdge(edgelist)
        # if vertices of that node do not belong to a group of already merged nodes, assign them to a new group
        if NodesTrack[edge[0] - 1] == 0 and NodesTrack[edge[1] - 1] == 0:
            NodesTrack[edge[0] - 1] = NewGroup
            NodesTrack[edge[1] - 1] = NewGroup
            # increase the NewGroup number
            NewGroup += 1
            # increase the amount of removed (merged) nodes by 1. And recurse
            RemovedNodes += 1
            return ContractNodes(edgelist)
        # in case only one vertex belong to a group, assign the other vertex to the same group
        elif NodesTrack[edge[0] - 1] == 0:
            NodesTrack[edge[0] - 1] = NodesTrack[edge[1] - 1]
            # increase the amount of removed (merged) nodes by 1. And recurse
            RemovedNodes += 1
            return ContractNodes(edgelist)
        elif NodesTrack[edge[1] - 1] == 0:
            NodesTrack[edge[1] - 1] = NodesTrack[edge[0] - 1]
            RemovedNodes += 1
            # increase the amount of removed (merged) nodes by 1. And recurse
            return ContractNodes(edgelist)
        # in case both nodes already belong to different groups, merge both groups
        elif NodesTrack[edge[0] - 1] != NodesTrack[edge[1] - 1]:
            # compute the 2 groups to be merged
            mingroup = min(NodesTrack[edge[0] - 1], NodesTrack[edge[1] - 1])
            maxgroup = max(NodesTrack[edge[0] - 1], NodesTrack[edge[1] - 1])
            # all nodes belonging to one group get assigned to the other group (to the one with minimum
            # value, it can be done the other way around too)
            for i in range(len(NodesTrack)):
                if NodesTrack[i] == maxgroup:
                    NodesTrack[i] = mingroup
            # increase the amount of removed (merged) nodes by 1. And recurse
            RemovedNodes += 1
            return ContractNodes(edgelist)
        # the remaining case is that both edges belong to the same group, which means that the edge was
        # already selected previously (or it is a self loop) from a merged node.
        # In any case, this a good moment to evaluate the edge list, and remove all previously selected
        # edges and self loops. Then recurse to get a new random edge. In this case, the RemovedNodes variable
        # is not increased as the only task here is to do a clean up of previous selected edges and self loops.
        else:
            k = []
            # for each edge check to which group its vertices belong to. If they belong to the same group
            # note its index in the list "k". edges which group = "0" mean they are still not assigned, so
            # exclude them
            for i in range(len(edgelist)):
                if NodesTrack[edgelist[i][0] - 1] == NodesTrack[edgelist[i][1] - 1] and\
                        NodesTrack[edgelist[i][0] - 1] != 0:
                    k += [i]
            reduced = ReduceList(edgelist, k)
            # remove all edges from the list whose index has been noted in "k"
            return ContractNodes(reduced)

def main():
    global RemovedNodes
    global NodesTrack
    global NewGroup
    global NodesToBeRemoved
    # retrieve list of nodes
    nodelist = RetrieveNodeList()
    # amount of nodes to be removed: all but two
    NodesToBeRemoved = len(nodelist) - 2
    # Initialize an array to keep track of which group of "merged nodes" each node of
    # the original graph belongs to
    # create a list of edges providing the adjacency list of nodes
    listofalledges = TransformToEdgeList(nodelist)
    # To achieve a Probability of success of at least 1/n where n is the amount of nodes in the
    # original graph. The contraction algorithm needs to be run at least: ln(n) * n^2
    n = len(nodelist)
    N = int(math.log(n) * n ** 2)
    # initialize variable to keep track of the minimum value so far across each iteration
    minbefore = len(listofalledges)
    print("------------------START----------------------\n"
          "Edges to be removed: %d\n"
          "RanContraction will run %d times\n"
          "---------------------------------------------" % (NodesToBeRemoved, N))
    # Run the contraction algorithm N times
    for i in range(N):
        # initialize global variables for each recursion
        NodesTrack = [0] * len(nodelist)
        RemovedNodes = 0
        NewGroup = 1
        # Call the ContractNodes algorithm
        result = ContractNodes(copy.deepcopy(listofalledges))
        # Compute the minimum result achieved so far
        minbefore = min(result, minbefore)
        # output information of each iteration
        print("Completed: %.2f %%\n"
              "Min-Cut of iteration %d: %d\n"
              "Min-Cut so far: %d\n"
              "Probability of success so far: At least %.3f %%\n"
              "---------------------------------------------"
              % (round((i + 1) / N * 100, 2), (i + 1), result, minbefore,
                 100 * (1 - (1 - 1 / n ** 2) ** (i + 1))))
    # output final result and some information
    print("\n------------------ENDED----------------------\n"
          "The computed Min-Cut value after %d iterations is: %d\n"
          "* With a probability of success of: At least %.3f %%\n"
          "---------------------------------------------"
          % (N, minbefore, 100 * (1 - (1 - 1 / n ** 2) ** N)))

# run
main()








