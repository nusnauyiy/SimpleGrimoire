bound=$1

if [ $# -eq 1 ]
then
	for bench in calculator cgidecode mathexpr microjson sexpr urlparse; do
		for i in $bound; do
			python3 search.py external ./eval-examples/$bench/$bench.sh eval-examples/$bench/train_set eval-examples/$bench/new-$bench-$i.log
			python3 eval.py external -n 50 ./eval-examples/$bench/$bench.sh unified_test_set/$bench/test_set eval-examples/$bench/new-$bench-$i.log
		done
	done
fi

if [ $# -eq 2 ]
then
	bench=$2
	for i in $bound; do
		python3 search.py external ./eval-examples/$bench/$bench.sh eval-examples/$bench/train_set eval-examples/$bench/new-$bench-$i.log
		python3 eval.py external -n 50 ./eval-examples/$bench/$bench.sh unified_test_set/$bench/test_set eval-examples/$bench/new-$bench-$i.log
	done	
fi
