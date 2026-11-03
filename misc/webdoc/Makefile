# Generate web documentation for https://foomuuri.foobar.fi/

.PHONY: all version worktree clean distclean

all: distclean
	mkdir final
	$(MAKE) version VERSION=0.27 HASH=cdfd867
	$(MAKE) version VERSION=0.28 HASH=38c5d4a
	$(MAKE) version VERSION=0.29 HASH=81c54c3
	$(MAKE) version VERSION=0.30 HASH=8a6de6c
	$(MAKE) version VERSION=0.31 HASH=8a6de6c
	$(MAKE) version VERSION=0.32 HASH=9f850bf
	$(MAKE) version VERSION=0.33 HASH=v0.33
	$(MAKE) version VERSION=0.34 HASH=359b934
	$(MAKE) version VERSION=development HASH=HEAD
	cp versions.json robots.txt final/
	ln -s $(shell jq -r '.[] | select(.version == "latest") | .title | ltrimstr("v")' versions.json) final/latest
	ln -s latest/sitemap.xml final/
	$(MAKE) clean

version: clean
	(cd ../.. && git archive $(HASH) docs/) | tar --extract
	[ -f docs/zensical.toml ] || cat docs/nav.toml common.toml > docs/zensical.toml
	mv docs/zensical.toml .
	zensical build --strict
	sed -i -e "/<.loc>$$/a \\        <lastmod>$$(git show -s --format=%cI $(HASH))</lastmod>" site/sitemap.xml
	find site -exec touch --date="$$(git show -s --format=%ci $(HASH))" {} \;
	mv site final/$(VERSION)

worktree: clean
	cp -a ../../docs docs
	mv docs/zensical.toml .
	zensical build --strict

clean:
	rm -rf .cache zensical.toml docs site

distclean: clean
	rm -rf final
