while IFS="" read -r p || [ -n "$p" ]
do
    rm $p
    mv "$p.orig" $p
done < dynapyt_files.txt