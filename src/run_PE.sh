#!/bin/bash
MINCS=$1
WORK_DIR=${15}
SRC=${16}

echo "Classification Start"
cat $WORK_DIR/SVC_debug/allClusters.txt | awk '$2 >= '$MINCS'' > $WORK_DIR/SVC_debug/allClusters.thresh.txt
sort -k4,4 -k5,5n $WORK_DIR/SVC_debug/allClusters.thresh.txt > $WORK_DIR/SVC_debug/allClusters.ls.txt
sort -k7,7 -k8,8n $WORK_DIR/SVC_debug/allClusters.thresh.txt > $WORK_DIR/SVC_debug/allClusters.rs.txt
time (python $SRC/classifySVs_v28.py $2 $3 $4 $WORK_DIR/SVC_debug)

#time python $SRC/qualifyDeletions.py $7
#mv $WORK_DIR/SVC_debug/All_Variants_DC.txt $WORK_DIR/SVC_debug/All_Variants.txt

if [ $6 -eq 1 ]
then
	python $SRC/SetCover_mq.py $5 $8 ${10} ${11} ${14} $WORK_DIR/SVC_debug $WORK_DIR/SVC_debug/variantMap.pe.txt $WORK_DIR/SVC_debug/allVariants.pe.txt
else
	python $SRC/DisjointSetCover.py $WORK_DIR/SVC_debug $WORK_DIR/SVC_debug/variantMap.pe.txt $WORK_DIR/SVC_debug/allVariants.pe.txt
fi

python $SRC/WriteBed.o2.py $WORK_DIR/SVC_debug/variants.uniqueFilter.txt $WORK_DIR/SVC_results $WORK_DIR/SVC_debug $WORK_DIR/SVC_debug/allVariants.pe.txt

if [ -d $WORK_DIR/SVC_results/pe_results ]
then
	rm -r $WORK_DIR/SVC_results/pe_results
fi
mkdir $WORK_DIR/SVC_results/pe_results
mv $WORK_DIR/SVC_results/*.bedpe $WORK_DIR/SVC_results/pe_results
