.PHONY: all

all:
	rm -f iplist-cache.json
	$(RUN) ../../src/foomuuri --set=etc_dir=. --set=share_dir=../../etc --set=state_dir=. --set=run_dir=. --set=nft_bin=true iplist refresh
	: # Normalize timestamps
	: # Remove localhost's IPv6 as not all systems have it
	: # Remove tailing comma in localhost's IPv4 after removing IPv6 entry
	jq --sort-keys . iplist-cache.json | \
		sed -E 's/[1-3][0-9]{9}/1800000000/; /"::1"/d; /"127.0.0.1"/ s/,//' > iplist-cache.json.2
	mv iplist-cache.json.2 iplist-cache.json
	diff -u golden-cache-json.txt iplist-cache.json
