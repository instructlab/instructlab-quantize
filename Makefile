# SPDX-License-Identifier: Apache-2.0

CMAKE_ARGS ?=

UNAME_MACHINE = $(shell uname -m | tr A-Z a-z)
UNAME_OS = $(shell uname -s | tr A-Z a-z)
QUANTIZE = build/quantize-$(UNAME_MACHINE)-$(UNAME_OS)
LLAMA_BUILDDIR = build/llama.cpp-$(UNAME_MACHINE)-$(UNAME_OS)
LLAMA_DIR = llama.cpp


.PHONY: all
all: test $(QUANTIZE)

.PHONY: test
test:
	tox p

.PHONY: fix
fix:
	tox -e format --
	tox -e ruff -- --fix

.PHONY: clean
clean:
	rm -rf .tox .ruff_cache dist build

$(LLAMA_BUILDDIR)/Makefile: $(LLAMA_DIR)/CMakeLists.txt
	@mkdir -p $(dir $@)
	CMAKE_ARGS="$(CMAKE_ARGS)" cmake -S $(dir $<) -B $(dir $@)

$(LLAMA_BUILDDIR)/bin/quantize: $(LLAMA_BUILDDIR)/Makefile
	cmake --build $(dir $<) --parallel 2 --config Release --target quantize

.PHONY: quantize
quantize: $(QUANTIZE)

$(QUANTIZE): $(LLAMA_BUILDDIR)/bin/quantize
	cp -a $< $@
