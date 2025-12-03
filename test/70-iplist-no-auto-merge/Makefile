.PHONY: all

all:
	../../src/foomuuri --set=etc_dir=. --set=share_dir=../../etc --set=state_dir=. --set=run_dir=. --set=nft_bin=true iplist refresh
	diff -u golden-cache-json.txt iplist-cache.json
