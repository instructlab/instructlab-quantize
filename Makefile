# SPDX-License-Identifier: Apache-2.0

CMAKE_ARGS ?=
QUANTIZE = build/quantize
LLAMA_BUILDDIR = build/llama.cpp
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
	cmake --build $(dir $<) --config Release --target quantize

$(QUANTIZE): $(LLAMA_BUILDDIR)/bin/quantize
	cp -a $< $@
