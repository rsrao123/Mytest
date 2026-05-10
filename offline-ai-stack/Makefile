PLAN ?= PLAN.md
CREWS := $(HOME)/offline-ai-stack/crews
SCRIPTS := $(HOME)/offline-ai-stack/scripts

plan-ceo-review:
	python $(CREWS)/exec_review.py --role ceo --plan $(PLAN)

plan-eng-review:
	python $(CREWS)/exec_review.py --role eng --plan $(PLAN)

plan-design-review:
	python $(CREWS)/exec_review.py --role design --plan $(PLAN)

plan-all-reviews:
	python $(CREWS)/exec_review.py --role all --plan $(PLAN)

review:
	git diff main > /tmp/change.diff
	python $(CREWS)/code_review.py /tmp/change.diff

qa:
	bash $(SCRIPTS)/security_scan.sh
	pytest -q

ship:
	python $(CREWS)/exec_review.py --role release --plan $(PLAN)
	@echo "Run 'git push' if release manager approved."

mem-recall:
	python $(SCRIPTS)/claude_mem_local.py recall $$(basename $$(pwd)) "$(Q)"
