all: foomuuri.8 prometheus-foomuuri-exporter.1

%.1: %.md
	pandoc --standalone --to=man $^ --output $@

%.8: %.md
	pandoc --standalone --to=man $^ --output $@
