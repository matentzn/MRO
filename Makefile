OBO = http://purl.obolibrary.org/obo
LIB = lib

tables = external core genetic-locus haplotype serotype chain molecule haplotype-molecule serotype-molecule mutant-molecule evidence chain-sequence
TSVFiles = $(foreach o,$(tables),ontology/$(o).tsv)
templates = $(foreach i,$(TSVFiles),--template $(i))

# core
mro.owl: mro-import.owl index.tsv $(TSVFiles) ontology/metadata.ttl
	robot merge \
	--input mro-import.owl \
	template \
	--prefix "MRO: $(OBO)/MRO_" \
	--prefix "REO: $(OBO)/REO_" \
	--template index.tsv \
	$(templates) \
	--merge-before \
	reason --reasoner HermiT \
	--remove-redundant-subclass-axioms false \
	annotate \
	--ontology-iri "$(OBO)/mro.owl" \
	--version-iri "$(OBO)/mro/$(shell date +%Y-%m-%d)/mro.owl" \
	--annotation owl:versionInfo "$(shell date +%Y-%m-%d)" \
	--annotation-file ontology/metadata.ttl \
	--output $@

# extended version for IEDB use
mro-iedb.owl: mro.owl ontology/iedb.tsv ontology/iedb-manual.tsv
	robot template \
	--prefix "MRO: $(OBO)/MRO_" \
	--input $< \
	--template ontology/iedb.tsv \
	--template ontology/iedb-manual.tsv \
	--merge-before \
	--output $@

# import
mro-import.owl: ontology/import.txt $(LIB)/ro.owl $(LIB)/obi.owl $(LIB)/eco.owl
	robot merge \
	--input $(LIB)/eco.owl \
	--input $(LIB)/obi.owl \
	--input $(LIB)/ro.owl \
	extract \
	--prefix "REO: $(OBO)/REO_" \
	--upper-term "GO:0008150" \
	--upper-term "IAO:0000030" \
	--upper-term "OBI:1110128" \
	--upper-term "ECO:0000000" \
	--upper-term "BFO:0000040" \
	--upper-term "PR:000000001" \
	--lower-terms $< \
	--output $@

# fetch ontology dependencies
$(LIB)/%:
	mkdir -p $(LIB)
	cd $(LIB) && curl -LO "$(OBO)/$*"


# generate files for IEDB

build:
	mkdir -p $@

build/mhc_allele_restriction.csv: mro-iedb.owl src/mhc_allele_restriction.rq | build
	robot query --input $(word 1,$^) --select $(word 2,$^) $@

build/mhc_allele_restriction.tsv: src/clean.py build/mhc_allele_restriction.csv | build
	python3 $^ \
	> $@

build/names.csv: mro-iedb.owl src/names.rq | build
	robot query --input $(word 1,$^) --select $(word 2,$^) $@.tmp
	tail -n+2 $@.tmp | dos2unix > $@
	rm $@.tmp

build/search.csv: mro-iedb.owl src/search.rq | build
	robot query --input $(word 1,$^) --select $(word 2,$^) $@.tmp
	tail -n+2 $@.tmp | dos2unix > $@
	rm $@.tmp

.PHONY: check
check: build/mhc_allele_restriction.tsv
	diff reference/mhc_allele_restriction.tsv build/mhc_allele_restriction.tsv

.PHONY: clean
clean:
	rm -f mro.owl mro-iedb.owl mro-import.owl
	rm -rf build
