import numpy as np
import random

def input(path):
    try:
        f=open(path,'r')
        txt=f.readlines()
        NodeNum=int(txt[0].split()[0])
        print "The number of nodes is",NodeNum
        EdgeNum=int(txt[0].split()[1])
        print "The number of edges is",EdgeNum
        AdjaceMatrix=np.zeros((NodeNum,NodeNum))
        for line in txt[1:len(txt)-1]:
            row=str.split(line)
            FormerNode=int(row[0])
            #print FormerNode
            NextNode=int(row[1])
            #print NextNode
            Probability=float(row[2])
            AdjaceMatrix[FormerNode-1][NextNode-1]=Probability
            #print AdjaceMatrix[FormerNode-1][NextNode-1]

        return AdjaceMatrix, NodeNum
    except IOError:
        print 'Error: file not found'
    finally:
        f.close()

"""This function take in one single seed, adjacementMatrix, ActivityState 
and find all the inactive neighbors
and store them into a list, 
also returns a list which stores the probability of the seed to active this neighbor"""
def find_inactive_neighbor(seed,AdjaceMat,ActivityState):
    neighbor=[]
    inactive_neighbor=[]
    prob_to_neighbor=[]# the probability to active this neighbor
    for i in range(0,Nodenum):
        if (AdjaceMat[seed-1][i]!=0):
               newNeighbor=i+1
               neighbor.append(newNeighbor) #get the neighbor list of the seed
    #print neighbor
    for i in range(0,len(neighbor)):
        if (ActivityState[neighbor[i]-1]==0):
            new_inactive_neighbor=neighbor[i]
            inactive_neighbor.append(new_inactive_neighbor) #get the inactive list of the seed
    #print inactive_neighbor
    for i in range(0,len(inactive_neighbor)):
        prob_to_neighbor.append(AdjaceMat[seed-1][inactive_neighbor[i]-1])
   # print prob_to_neighbor
    return inactive_neighbor,prob_to_neighbor #The number of nodes in this list is the real number of the nodes
"""
This function takes in a seed, the AdjacementMatrix, the ActivityState
and first, get the neighbors of the seed
then, get the active ones among these neighbors 
finally, calculate and returns the sum of weights
"""
def find_active_neighbor(seed,AdjaceMat,ActivityState):
    neighbor=[]
    active_neighbor=[]
    sum_of_weight=0
    for i in range(0, Nodenum):
        if (AdjaceMat[i][seed - 1] != 0):
            newNeighbor = i + 1
            neighbor.append(newNeighbor)  # get the neighbor list of the seed
    #print neighbor
    for i in range(0, len(neighbor)):
        if (ActivityState[neighbor[i] - 1] != 0):
            new_active_neighbor = neighbor[i]
            active_neighbor.append(new_active_neighbor)  # get the inactive list of the seed
    for i in range(0,len(active_neighbor)):
        sum_of_weight = sum_of_weight + AdjaceMat[active_neighbor[i] - 1][seed - 1]
    #print  sum_of_weight
    return sum_of_weight
            # print inactive_neighbor

"""
A one IC Sample
"""
def IC(AdjaceMat,SeedSet):

    ActivitySet = SeedSet
    ActivityState = np.zeros(Nodenum)  # Store the states of all the nodes
    for i in ActivitySet:
        temp = i
        ActivityState[temp - 1] = 1.0  # Set the state of the seed to active.
        # print ActivityState
        # find_inactive_neighbor(SeedSet[0],ActivitySet,AdjaceMat)
    count = ActivitySet.__len__()  # print count
    while (ActivitySet.__len__() != 0):
        newActivitySet = []
        for seed in ActivitySet:
            inactive_neighbor, prob_to_neighbor = find_inactive_neighbor(seed,AdjaceMat,ActivityState)
            for i in range(0, len(inactive_neighbor)):
                randomNum = random.random()
                if (randomNum < prob_to_neighbor[i]):
                    ActivityState[inactive_neighbor[i] - 1] = 1.0
                    newActivitySet.append(inactive_neighbor[i])

        count = count + newActivitySet.__len__()
        ActivitySet = newActivitySet

    #print count
    return count
"""
One LT Sample
"""
def LT(AdjaceMat,SeedSet):
    ActivitySet=SeedSet
    ActivityState = np.zeros(Nodenum)  # Store the states of all the nodes
    for i in ActivitySet:
        temp = i
        ActivityState[temp - 1] = 1.0  # Set the state of the seed to active.
        # print ActivityState
        # find_inactive_neighbor(SeedSet[0],ActivitySet,AdjaceMat)
    threshold = np.zeros(Nodenum)
    for i in range(0,len(threshold)):
        threshold[i]=random.random()
    #print threshold
    count = ActivitySet.__len__()
    while(ActivitySet.__len__() != 0):
        newActivitySet=[]
        for seed in ActivitySet:
            inactive_neighbor,prob_to_neighbor=find_inactive_neighbor(seed,AdjaceMat,ActivityState)
            #print inactive_neighbor
            for i in range(0,len(inactive_neighbor)):
                w_total=find_active_neighbor(inactive_neighbor[i],AdjaceMat,ActivityState)
               # print w_total
                temp=inactive_neighbor[i]-1
               # print temp
                w_single=threshold[temp]
                if(w_total>=w_single):
                    ActivityState[inactive_neighbor[i] - 1]=1.0
                    newActivitySet.append(inactive_neighbor[i])
        count = count + newActivitySet.__len__()
        ActivitySet=newActivitySet
    #print count
    return count




if __name__=='__main__':

    #input('network.txt')
    AdjaceMat,Nodenum = input('network.txt')
    #print AdjaceMat,Nodenum
    SeedSet = [12, 1, 14, 15]


    #IC(AdjaceMat,SeedSet)
    sum1=0
    N=10000
    for i in range(0,N):
      oneSample=LT(AdjaceMat,SeedSet)
      sum1=sum1+oneSample
    print "(LT)The average number of spread people is",sum1/N

    sum2=0

    for i in range(0,N):
      oneSample=IC(AdjaceMat,SeedSet)
      sum2=sum2+oneSample
    print "(IC)The average number of spread people is",sum2/N








