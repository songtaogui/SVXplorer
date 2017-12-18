# 12/16/16
# Set Cover Algorithms to Minimize number of SVs that account for all PEMs pointing to them

import math
import os
import sys
from collections import Counter

FILE = "../results/text/VariantMap.txt"

#disjThresh = int(sys.argv[1])
MAP_THRESH = int(sys.argv[2])
ignoreRD = 1
RD_VAR_NUM = int(sys.argv[3]) #3000000
RD_Frag = int(sys.argv[4])
MQ_HASH = {}

def formHash():

	f=open("../results/text/All_Discords_P_S.txt","r")
	for line in f:
		temp = int(line.split()[0])
		temp2 = int(line.split()[-1])
		#include only primary alignments; assume if fragment unique for a variant, then it is primary
		#we are ensured that primary alignment of the read clears MAP_THRESH, and relative AS of secondary is very close by default
		if temp not in MQ_HASH and temp2 >= MAP_THRESH:
			MQ_HASH[temp] = 1
	
def DisjointAlg(fragmentList, nSetsR, disjThresh):

    N_potSVs = 0
    counter = 0
    taggedList=[] # keeps track of shared elements
    setCover = []
    listSize = []
    disjointness = [0]*nSetsR
    pickV = [0]*nSetsR
    varNum = []
    #results = [0]*(max(fragmentList) + 1)

    # fragment numbering starts with 1

    #claimed = [0]*(1+max(fragmentList)) # change to n unique frags if saves time

    formHash()
    fp=open(FILE,"r")
    fp2=open("../results/text/DisjSetCover_S.txt","w")
    fp4=open("../results/text/mq0_variants.txt","w")
    fp5=open("../results/text/uniqueCount.txt","w")
    fp6=open("../results/text/All_Variants_SR.txt","r")

    x = Counter(fragmentList)
    # Obtain disjointness count
    # Assume any given fragment only appears once in set list
    for line in fp:

        currentSet = map(int, line.split())
        varNum.append(currentSet[0])
	currentSet = currentSet[1:] 	

        for elem in currentSet:
		
		#pick those supported by RD automatically		
		if elem >= RD_Frag:
		
			if x[elem] == 1:
				disjointness[counter]+=1
			pickV[counter] = 2

		#if SR, no secondaries so is above MQ_THRESH automatically
		elif x[elem] == 1:

	            disjointness[counter]+=1

		    #require at least 1 MQ > some_thresh support
		    if elem in MQ_HASH or elem < 0:
			pickV[counter] = 1

		if disjointness[counter] == disjThresh:
			break
	counter+=1

    n_sr_supp = 0
    n_pe_supp = 0
    for g,item in enumerate(disjointness):

	sr_supp = 0
	pe_supp = 0
	for line in fp6:
		if line.split()[11].find("PE_SR") != -1:
			sr_supp = 1
		elif line.split()[11].find("PE") != -1:
			pe_supp = 1
		break
	# RD CNVs do not use same support threshold
        if (item >= disjThresh and pickV[g] == 1) or (item >= 1 and pickV[g] == 2):
           fp2.write("%s\n" %varNum[g]) 
	   if sr_supp:
		n_sr_supp+=1
	   elif pe_supp:
	   	n_pe_supp+=1
	#make list of variants not picked
	if varNum[g] < RD_VAR_NUM:
	   fp5.write("%s %s\n" %(varNum[g], disjointness[g]))

    return 1.0*n_sr_supp/n_pe_supp

    #potSVs = [item for item in disjointness if item > disjThresh]        
    
def ReadFile(filename):

    allFrags = []
    counter=0
    f=open(filename, 'r')
    for line in f:

        parsed = map(int, line.split())
        counter = counter + 1
        for x in parsed[1:]:
            allFrags.append(x)

    f.close()
    return allFrags, counter
      
    
if __name__ == "__main__":  

   [allFrags, nSetsR] = ReadFile(FILE)
   
   #decide best unique support threshold based on data set
   max_call_ratio = 0
   print "Calculating best threshold for unique support to call final variants"

   for x in range(3,7):
	print x, "...?"
   	srpe_call_ratio =  DisjointAlg(allFrags, nSetsR, x)
   	if srpe_call_ratio > max_call_ratio:
		max_call_ratio = srpe_call_ratio
		max_call_dthresh = x
   print "Best threshold determined to be", max_call_dthresh, "supporting fragments per variant."
   #final best call
   srpe_call_ratio =  DisjointAlg(allFrags, nSetsR, max_call_dthresh)
   
   #WriteMappings(DisjFM, "FragMapD.txt")
 
   