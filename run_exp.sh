#!/bin/sh
exp=exp

rm -rf $exp
mkdir $exp

train=data/train.f
#train=data/merge.train.f
test_set="data/test.f data/test_sy.f data/test_vip.f"
#test_set="data/merge.test.f data/merge.test_sy.f data/merge.test_vip.f"

#input file
feature=data/feature.meta
active=active.meta

#output file
model=tree_model
eval_train=result_train
model_weight=model_weight
multi_test=false

##default input parameter
test_num=1

##the fv feature start index
fv_index=4

if [ ! -z $1 ]
then
    multi_test=true
    test_num=$1
    echo "# running in multi-test mode, round of tests: $1"
    echo "Good Luck! You are on the money"
fi

echo "# train="$train, "test="${test_set}, "model="$model

echo "# select active feature & convert data format"
echo "# processing training set"
echo "#   $train"
python2 ./select.py -m $feature -a $active -f $fv_index < $train > $exp/train_active
python2 ./dense.py $fv_index < $exp/train_active > $exp/train_dense

echo "# processing test sets"
for t in $test_set
do
    echo "#   $t"
    t_norm=`echo $t | gawk -F"/" '{print $NF }'`
    python2 ./select.py -m $feature -a $active -f $fv_index < $t > $exp/${t_norm}.active
    #./dense.py < $exp/${t_norm}.active > $exp/${t_norm}.dense
done

for (( i=0; i<test_num; i++))
do
    if $multi_test
    then
        echo "# running multiple test, round: $i"
    fi
    echo "# model training in progress"
    ./tree_models_train train.cfg -fileTrain $exp/train_dense -fileModel $exp/$model
    echo "# model training completed, saved to $exp/$model"

    echo "# running model feature weighting analysis"
    python2 ./get_feature_weight.py $exp/train_dense $exp/$model $active > $exp/$model_weight 2>$exp/$model_weight.log
    echo "# model feature weighting analysis done, result: $exp/$model_weight"
    
    echo "# evaluation in progress"
    python2 ./eval.py -m $exp/$model -i $exp/train_active -o $exp/$eval_train -f $fv_index
    printf  "\n############## train ##############\n"
    cat $exp/$eval_train.stat
    tail -n1 $exp/$eval_train.stat >> $exp/$eval_train.all

    for t in $test_set
    do
        t_norm=`echo $t | gawk -F"/" '{print $NF}'`
        t_output="$exp/${t_norm}_$i"
        python2 ./eval.py -m $exp/$model -i $exp/${t_norm}.active -o $t_output -f $fv_index
        printf "\n############## test($t)  ##############\n"
        cat $t_output.stat
        cat $t_output.stat >> $exp/${t_norm}.stat_all
        tail -n1 $t_output.stat >> $exp/${t_norm}.all

    done

    echo "# evaluation completed"

    echo "# backup"
    cp train.cfg $exp
    cp $train    $exp
    for t in $test_set
    do
        cp $t     $exp
    done
    cp $active   $exp
    cp $feature  $exp
    echo
done

if $multi_test
then
    echo "###########Multiple Test Result(Average of all runs###########"
    
    printf "%-35s%-15s%-15s%-15s%-15s\n" "DataSet" "Precision" "Recall" "F-Measure" "Entropy" >> $exp/stat
    
    for t in $test_set
    do
        t_norm=`echo $t | gawk -F"/" '{print $NF}'`
        printf "%-35s" $t_norm >> $exp/stat
        awk  'BEGIN{OFS="\t"; p=0.0; r=0.0; f=0.0; e=0.0;} {p+=$1; r+=$2; f+=$3; e+=$4;} END{printf("%-15.4f%-15.4f%-15.4f%-15.4f\n", p/NR, r/NR, f/NR, e/NR)}' $exp/${t_norm}.all >> $exp/stat
    done

    cat $exp/stat
fi
