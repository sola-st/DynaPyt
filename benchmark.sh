while read repo test; do
    bash ./experiment.sh $repo $test TraceAll
    bash ./experiment.sh $repo $test original
done < benchmark.txt