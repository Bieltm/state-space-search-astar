#!/bin/bash

sortida="resultats.txt"
rm -f $sortida

# Debt settlement
for fitxer in problems/payments/*; do
    for algorisme in tree-bfs graph-bfs tree-ucs graph-ucs; do
        echo "$fitxer - $algorisme" >> $sortida
        timeout 300 hlog-search -p problems/debt_settlement.py -a $algorisme --file_ "$fitxer" -v none >> $sortida 2>&1
    done
done

# Join order
for fitxer in problems/queries/*; do
    for algorisme in tree-bfs graph-bfs tree-ucs graph-ucs; do
        echo "$fitxer - $algorisme" >> $sortida
        timeout 300 hlog-search -p problems/join_order.py -a $algorisme --file_ "$fitxer" -v none >> $sortida 2>&1
    done
done

# Pacman
for mapa in problems/layouts/*.lay problems/layouts/wc3/*.lay; do
    for algorisme in tree-bfs graph-bfs tree-ucs graph-ucs; do
        echo "$mapa - $algorisme" >> $sortida
        timeout 300 hlog-search -p problems/pacman.py -a $algorisme --layout "$mapa" -v none >> $sortida 2>&1
    done

    for heuristica in ManhattanHeuristic EuclideanHeuristic; do
        for algorisme in tree-astar graph-astar; do
            echo "$mapa - $algorisme - $heuristica" >> $sortida
            timeout 300 hlog-search -p problems/pacman.py -a algorithms/astar.py:$algorisme -H $heuristica --layout "$mapa" -v none >> $sortida 2>&1
        done
    done
done