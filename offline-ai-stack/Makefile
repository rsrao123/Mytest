PLAN ?= PLAN.md
STACK := $(HOME)/offline-ai-stack
CREWS := $(STACK)/crews
SCRIPTS := $(STACK)/scripts
PROJECT ?= $(shell basename $$(pwd))

.PHONY: help offline-prep stage-bundle import-bundle os-harden \
        offline-doctor offline-doctor-strict airgap-test hf-audit \
        bring-up tear-down compose-up compose-down ingest voice \
        plan-ceo-review plan-eng-review plan-design-review plan-all-reviews \
        review security-review qa ship mem-recall eval

help:
	@echo "Two-machine air-gapped flow:"
	@echo "  STAGING (connected machine):"
	@echo "    offline-prep        Pre-cache scanner DBs, models, docker images, telemetry-off"
	@echo "    stage-bundle        Bundle everything into BUNDLE_DIR for transfer to air-gapped target"
	@echo "  TARGET (air-gapped machine):"
	@echo "    import-bundle BUNDLE=<dir>   Consume the bundle; no internet needed"
	@echo "    os-harden           sudo: mask Ubuntu's NTP / snap / unattended-upgrades / whoopsie / apport"
	@echo ""
	@echo "Verification (run on target):"
	@echo "  hf-audit            Structural: every model present + no repo-ID surprises in runtime code"
	@echo "  offline-doctor      Observed: passive 30s probe for non-loopback egress"
	@echo "  offline-doctor-strict  Adversarial: iptables blocks egress during a 30s probe (sudo)"
	@echo "  airgap-test         Hardest: drop ALL non-loopback OUTPUT, run full smoke (sudo, ~90s)"
	@echo "  bring-up            Start vLLM + docker stack (Section 21)"
	@echo "  tear-down           Stop everything (preserves volumes)"
	@echo "  compose-up          docker compose up -d"
	@echo "  compose-down        docker compose down"
	@echo "  ingest DIR=<path>   Ingest a project into Chroma project-memory"
	@echo "  voice FILE=<wav>    Transcribe an audio file with faster-whisper"
	@echo "  plan-ceo-review     Plan review by CEO agent"
	@echo "  plan-eng-review     Plan review by Engineering Lead"
	@echo "  plan-design-review  Plan review by Design Lead"
	@echo "  plan-all-reviews    All exec roles in parallel"
	@echo "  review              4-agent parallel code review on git diff main"
	@echo "  security-review     Standalone security agent on git diff main"
	@echo "  qa                  security scanners + pytest (all offline)"
	@echo "  ship                Release-manager review (PLAN=...)"
	@echo "  mem-recall Q='...'  Recall past-session context for current project"
	@echo "  eval                promptfoo eval against vLLM endpoints"

bring-up:
	bash $(SCRIPTS)/bring-up.sh

tear-down:
	bash $(SCRIPTS)/tear-down.sh

compose-up:
	cd $(STACK) && docker compose up -d

compose-down:
	cd $(STACK) && docker compose down

ingest:
	@test -n "$(DIR)" || (echo "Set DIR=<project_dir>" && exit 2)
	python $(SCRIPTS)/ingest.py $(DIR)

voice:
	@test -n "$(FILE)" || (echo "Set FILE=<audio>" && exit 2)
	python $(SCRIPTS)/voice_transcribe.py $(FILE)

offline-prep:
	bash $(SCRIPTS)/offline-prep.sh

stage-bundle:
	bash $(SCRIPTS)/stage-bundle.sh

import-bundle:
	@test -n "$(BUNDLE)" || (echo "Set BUNDLE=/path/to/bundle-dir" && exit 2)
	bash $(SCRIPTS)/import-bundle.sh $(BUNDLE)

offline-doctor:
	bash $(SCRIPTS)/offline-doctor.sh --probe-workload 30

offline-doctor-strict:
	bash $(SCRIPTS)/offline-doctor.sh --strict --probe-workload 30

hf-audit:
	bash $(SCRIPTS)/hf-audit.sh

os-harden:
	sudo bash $(SCRIPTS)/os-harden-offline.sh

airgap-test:
	sudo bash $(SCRIPTS)/airgap-test.sh

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

security-review:
	git diff main > /tmp/change.diff
	python $(CREWS)/security_review.py /tmp/change.diff

qa:
	bash $(SCRIPTS)/security_scan.sh
	pytest -q

ship:
	python $(CREWS)/exec_review.py --role release --plan $(PLAN)
	@echo "Run 'git push' if release manager approved."

mem-recall:
	@test -n "$(Q)" || (echo "Set Q='question'" && exit 2)
	python $(SCRIPTS)/claude_mem_local.py recall $(PROJECT) "$(Q)"

eval:
	cd $(STACK) && promptfoo eval
