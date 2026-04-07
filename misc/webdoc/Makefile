# Generate web documentation for https://foomuuri.foobar.fi/

.PHONY: all version clean distclean

all: distclean
	mkdir final
	$(MAKE) version VERSION=0.27 HASH=cdfd86778a61d1ed81eaad50dbebc54bd7e9452e
	$(MAKE) version VERSION=0.28 HASH=38c5d4a1097f30cc2addd093b66c4a82e0e95763
	$(MAKE) version VERSION=0.29 HASH=81c54c327f79baffdb7246d0bc637df821645d31
	$(MAKE) version VERSION=0.30 HASH=8a6de6c5e61f62d84cbe9b24cfb742f9c9a65616
	$(MAKE) version VERSION=0.31 HASH=8a6de6c5e61f62d84cbe9b24cfb742f9c9a65616
	$(MAKE) version VERSION=0.32 HASH=9f850bfa3d55fca9972ff4556fece079e6c10d44
	$(MAKE) version VERSION=development HASH=HEAD
	cp versions.json final/
	ln -s $(shell jq -r '.[] | select(.version == "latest") | .title | ltrimstr("v")' versions.json) final/latest
	ln -s latest/sitemap.xml final/
	$(MAKE) clean

version:
	rm -rf docs
	(cd ../.. && git archive $(HASH) docs/) | tar --extract
	cat docs/nav.toml common.toml > zensical.toml
	zensical build
	mv site final/$(VERSION)

clean:
	rm -rf .cache zensical.toml docs site

distclean: clean
	rm -rf final
