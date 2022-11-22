#!/bin/bash
# Usage: bash analyze.sh --source <directory or file> --analysis <name of analysis>
# e.g.: bash analyze.sh --source test/targetPrograms/demo.py --analysis TraceAll

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s|--source) source="$2"; shift ;;
        -a|--analysis) analysis="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo $source
echo $analysis