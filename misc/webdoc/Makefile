# Generate web documentation for https://foomuuri.foobar.fi/

.PHONY: all version worktree clean distclean

OLD_FEATURES	= \"navigation.expand\",
NEW_FEATURES	= \"navigation.tabs\",\"navigation.footer\",\"toc.integrate\",

all: distclean
	mkdir final
	$(MAKE) version VERSION=0.27 HASH=cdfd86778a61d1ed81eaad50dbebc54bd7e9452e FEATURES='$(OLD_FEATURES)'
	$(MAKE) version VERSION=0.28 HASH=38c5d4a1097f30cc2addd093b66c4a82e0e95763 FEATURES='$(OLD_FEATURES)'
	$(MAKE) version VERSION=0.29 HASH=81c54c327f79baffdb7246d0bc637df821645d31 FEATURES='$(OLD_FEATURES)'
	$(MAKE) version VERSION=0.30 HASH=8a6de6c5e61f62d84cbe9b24cfb742f9c9a65616 FEATURES='$(OLD_FEATURES)'
	$(MAKE) version VERSION=0.31 HASH=8a6de6c5e61f62d84cbe9b24cfb742f9c9a65616 FEATURES='$(OLD_FEATURES)'
	$(MAKE) version VERSION=0.32 HASH=9f850bfa3d55fca9972ff4556fece079e6c10d44 FEATURES='$(OLD_FEATURES)'
	$(MAKE) version VERSION=development HASH=HEAD FEATURES='$(NEW_FEATURES)'
	cp versions.json robots.txt final/
	ln -s $(shell jq -r '.[] | select(.version == "latest") | .title | ltrimstr("v")' versions.json) final/latest
	ln -s latest/sitemap.xml final/
	$(MAKE) clean

version:
	rm -rf docs site
	(cd ../.. && git archive $(HASH) docs/) | tar --extract
	cat docs/nav.toml common.toml | sed s/@@FEATURES@@/$(FEATURES)/ > zensical.toml
	zensical build --strict
	sed -i -e "/<.loc>$$/a \\        <lastmod>$$(git show -s --format=%cI $(HASH))</lastmod>" site/sitemap.xml
	find site -exec touch --date="$$(git show -s --format=%ci $(HASH))" {} \;
	mv site final/$(VERSION)

worktree:
	rm -rf docs site
	cp -a ../../docs docs
	cat docs/nav.toml common.toml | sed s/@@FEATURES@@/$(NEW_FEATURES)/ > zensical.toml
	zensical build --strict

clean:
	rm -rf .cache zensical.toml docs site

distclean: clean
	rm -rf final
