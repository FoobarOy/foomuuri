.PHONY: all

all:
	rm -f iplist-cache.json
	$(RUN) ../../src/foomuuri --set=etc_dir=. --set=share_dir=../../etc --set=state_dir=. --set=run_dir=. --set=nft_bin=true iplist refresh
	sed -i -E 's/[1-3][0-9]{9}/1800000000/g' iplist-cache.json  # normalize relative refresh
	sed -i '/"::1":/d' iplist-cache.json  # remove IPv6
	sed -i -E 's/("127.0.0.1": 4000000000),/\1/' iplist-cache.json  # remove comma after removing IPv6 entry
	diff -u golden-cache-json.txt iplist-cache.json
