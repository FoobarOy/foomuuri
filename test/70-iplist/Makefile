.PHONY: all

all:
	rm -f iplist-cache.json
	$(RUN) ../../src/foomuuri --set=etc_dir=. --set=share_dir=../../etc --set=state_dir=. --set=run_dir=. --set=nft_bin=true iplist refresh
	sed -i -E 's/[1-3][0-9]{9}/1800000000/g' iplist-cache.json  # fix relative refresh
	sed -i -E 's/[5-9][0-9]{9}/4000000000/g' iplist-cache.json  # fix relative timeout to "forever" value
	diff -u golden-cache-json.txt iplist-cache.json
