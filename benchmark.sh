curr=$(pwd)
while read repo test; do
    cd $curr
    bash ./experiment.sh $repo $test TraceAll
    cd $curr
    bash ./experiment.sh $repo $test original
done < benchmark.txt