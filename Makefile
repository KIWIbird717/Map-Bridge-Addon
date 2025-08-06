.PHONY: build help

# Variables
PYTHON := poetry run python -m
BUILD_SCRIPT_PATH := scripts.build
BLENDER_RUNNER_SCRIPT := scripts.run_in_blender

# Output colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Available commands
	@echo "$(YELLOW)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Build project in zip archive
	@echo "$(GREEN)Run build scrip$(NC)"
	$(PYTHON) $(BUILD_SCRIPT_PATH)

run: ## Install addon to blender and launch blender with installed addon
	@echo "$(YELLOW)Installing addon into Blender...$(NC)"
	@echo "Build addon..."
	@make build
	@echo ""
	@echo "Open Blender with installed addon..."
	$(PYTHON) $(BLENDER_RUNNER_SCRIPT)