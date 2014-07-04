
'''
CCWP heuristic for arbitrary propagation probabilities.
'''

from __future__ import division
import networkx as nx
from heapq import nlargest
from copy import deepcopy
import os, json, multiprocessing, random
from runIAC import *

def findCC(G, Ep):
    # remove blocked edges from graph G
    E = deepcopy(G)
    edge_rem = [e for e in E.edges() if random.random() < (1-Ep[e])**(E[e[0]][e[1]]['weight'])]
    E.remove_edges_from(edge_rem)

    # initialize CC
    CC = dict() # each component is reflection of the number of a component to its members
    explored = dict(zip(E.nodes(), [False]*len(E)))
    c = 0
    # perform BFS to discover CC
    for node in E:
        if not explored[node]:
            c += 1
            explored[node] = True
            CC[c] = [node]
            component = E[node].keys()
            for neighbor in component:
                if not explored[neighbor]:
                    explored[neighbor] = True
                    CC[c].append(neighbor)
                    component.extend(E[neighbor].keys())
    return CC

def CCWP(G, k, Ep):
    '''
     Input:
     G -- undirected graph (nx.Graph)
     k -- number of nodes in seed set (int)
     p -- propagation probability among all edges (int)
     Output:
     scores -- scores of nodes according to some weight function (dict)
    '''
    scores = dict(zip(G.nodes(), [0]*len(G))) # initialize scores

    CC = findCC(G, Ep)

    # find ties for components of rank k and add them all as qualified
    sortedCC = sorted([(len(cc), cc_number) for (cc_number, cc) in CC.iteritems()], reverse=True)
    topCCnumbers = sortedCC[:k] # CCs we assign scores to
    L = sum([l for (l, _) in topCCnumbers])

    increment = 0
    # add ties of rank k (if len of kth CC == 1 then add all CCs)
    while k+increment < len(sortedCC) and sortedCC[k + increment][0] == sortedCC[k-1][0]:
        topCCnumbers.append(sortedCC[k + increment])
        increment += 1

    # assign scores to nodes in top Connected Components
    # prev_length  = topCCnumbers[0][0]
    # rank = 1
    for length, numberCC in topCCnumbers:
        # if length != prev_length:
        #     prev_length = length
        #     rank += 1
        # weighted_score = length
        weighted_score = 1.0/length
        # weighted_score = 1
        for node in CC[numberCC]:
            scores[node] += weighted_score
    return scores

def frange(begin, end, step):
    x = begin
    y = end
    while x < y:
        yield x
        x += step


if __name__ == '__main__':
    import time
    start = time.time()

    # read in graph
    G = nx.read_gpickle("../../graphs/hep.gpickle")
    print 'Read graph G'
    print time.time() - start

    #calculate initial set
    R = 500
    I = 250
    DROPBOX = "/home/sergey/Dropbox/Influence Maximization/"
    FILENAME = "TvsR_Random.txt"
    ftime = open('plotdata/time' + FILENAME, 'a+')
    DROPBOXftime = open(DROPBOX + 'plotdata/time' + FILENAME, 'w+')
    logfile = open('log.txt', 'w+')
    # print >>logfile, '--------------------------------'
    # print >>logfile, time.strftime("%c")

    # get propagation probabilities
    Ep = dict()
    with open("Ep_hep_random1.txt") as f:
        for line in f:
            data = line.split()
            Ep[(int(data[0]), int(data[1]))] = float(data[2])

    l2c = [[0,0]]

    R2T = [[0, 0]]
    pool = None
    pool2 = None

    for R in range(1, 500, 50):
        print "R:", R
        for length in range(150, 151, 5):
            time2length = time.time()
            print 'Start finding solution for length = %s' %length
            print >>logfile, 'Start finding solution for length = %s' %length
            time2S = time.time()

            print 'Start mapping...'
            time2map = time.time()
            # define map function
            def map_CCWP(it):
                return CCWP(G, length, Ep)
            # if pool == None:
            #     pool = multiprocessing.Pool(processes=None)
            Scores = map(map_CCWP, range(R))
            # print 'Finished mapping in', time.time() - time2map

            print 'Start reducing...'
            time2reduce = time.time()
            scores = {v: sum([s[v] for s in Scores]) for v in G}
            scores_copied = deepcopy(scores)
            S = []
            # penalization phase
            for it in range(length):
                maxk, maxv = max(scores_copied.iteritems(), key = lambda (dk, dv): dv)
                S.append(maxk)
                scores_copied.pop(maxk) # remove top element from dict
                for v in G[maxk]:
                    if v not in S:
                        # weight = scores_copied[v]/maxv
                        # print weight,
                        penalty = (1-Ep[(maxk, v)])**(G[maxk][v]['weight'])
                        scores_copied[v] = penalty*scores_copied[v]
            print S
            print >>logfile, json.dumps(S)
            print >>ftime, "%s %s" %(length, time.time() - time2S)
            # print 'Finished reducing in', time.time() - time2reduce
            print 'Finish finding S in %s sec...' %(time.time() - time2S)

            print 'Start calculating coverage...'
            def map_AvgIAC (it):
                return avgIAC(G, S, Ep, I)
            # TODO for some reason pool.map uses parameters from 1st iteration. Fix to use pool.map inside a loop.
            # if pool2 == None:
            #     pool2 = multiprocessing.Pool(processes=None)
            avg_size = 0
            time2avg = time.time()
            Ts = map(map_AvgIAC, range(4))
            print Ts
            avg_size = sum(Ts)/len(Ts)
            print 'Average coverage of %s nodes is %s' %(length, avg_size)
            print 'Finished averaging seed set size in', time.time() - time2avg

            l2c.append([length, avg_size])
            # with open('plotdata/plot' + FILENAME, 'w+') as fp:
            #     json.dump(l2c, fp)
            # with open(DROPBOX + 'plotdata/plot' + FILENAME, 'w+') as fp:
            #     json.dump(l2c, fp)
            #

            R2T.append([R, avg_size])
            with open('plotdata/' + FILENAME, 'w+') as fp:
                print >>fp, length
                json.dump(R2T, fp)
            with open(DROPBOX + 'plotdata/' + FILENAME, 'w+') as fp:
                print >>fp, length
                json.dump(R2T, fp)

            print 'Total time for length = %s: %s sec' %(length, time.time() - time2length)
            print '----------------------------------------------'

    ftime.close()
    logfile.close()

    print 'Total time: %s' %(time.time() - start)

    console = []