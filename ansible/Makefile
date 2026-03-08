.PHONY: help setup install test lint add-client remove-client show-config clean

# Змінні
PYTHON := python3
VENV := venv
ANSIBLE := ansible-playbook

help: ## Показати цю довідку
	@echo "Доступні команди:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Налаштувати проект (створити venv, встановити залежності)
	@echo "🚀 Налаштування проекту..."
	@./scripts/setup.sh

install: ## Встановити залежності
	@echo "📦 Встановлення залежностей..."
	@$(PYTHON) -m pip install -q --upgrade pip
	@$(PYTHON) -m pip install -q -r requirements.txt
	@ansible-galaxy collection install -r requirements.yml --force

test: ## Перевірити з'єднання з сервером
	@echo "🔌 Перевірка з'єднання..."
	@ansible wireguard_servers -m ping

lint: ## Перевірити Ansible файли
	@echo "🔍 Перевірка синтаксису..."
	@ansible-lint playbooks/*.yml || true
	@yamllint inventory/ || true

add-client: ## Додати клієнта (використання: make add-client [або make add-client IP=10.66.66.5])
	@if [ -z "$(IP)" ]; then \
		echo "🤖 Автоматичне призначення IP адреси..."; \
		$(ANSIBLE) playbooks/add_client.yml; \
	else \
		NAME="R6$$(echo $(IP) | cut -d. -f4)"; \
		echo "➕ Генерація ключів для $$NAME ($(IP))..."; \
		$(PYTHON) scripts/generate_keys.py $$NAME; \
		echo "➕ Додавання $$NAME на сервер..."; \
		$(ANSIBLE) playbooks/add_client.yml -e "client_ip=$(IP)"; \
	fi

remove-client: ## Видалити клієнта (використання: make remove-client IP=10.66.66.5)
	@if [ -z "$(IP)" ]; then \
		echo "❌ Використання: make remove-client IP=10.66.66.5"; \
		echo "   Ім'я клієнта буде згенеровано автоматично: R6{останній_октет}"; \
		exit 1; \
	fi
	@NAME="R6$$(echo $(IP) | cut -d. -f4)"; \
	echo "➖ Видалення $$NAME ($(IP)) з сервера..."; \
	$(ANSIBLE) playbooks/remove_client.yml -e "client_ip=$(IP)" -e "skip_confirmation=true"

show-config: ## Показати поточну конфігурацію сервера
	@echo "📋 Отримання конфігурації..."
	@$(ANSIBLE) playbooks/show_config.yml

generate-keys: ## Згенерувати ключі для клієнта (використання: make generate-keys NAME=peer4)
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Використання: make generate-keys NAME=peer4"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/generate_keys.py $(NAME)

bulk-add: ## Масово додати клієнтів з CSV (використання: make bulk-add FILE=clients.csv)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Використання: make bulk-add FILE=clients.csv"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/bulk_add_clients.py $(FILE)

get-public-key: ## Отримати публічний ключ з приватного (використання: make get-public-key KEY="...")
	@if [ -z "$(KEY)" ]; then \
		echo "❌ Використання: make get-public-key KEY=\"приватний_ключ\""; \
		exit 1; \
	fi
	@$(PYTHON) scripts/get_public_key.py "$(KEY)"

prepare-config: ## Додати SSH ключ до конфігурації клієнта (використання: make prepare-config NAME=peer4)
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Використання: make prepare-config NAME=peer4 [KEY=~/.ssh/id_ed25519.pub]"; \
		exit 1; \
	fi
	@./scripts/prepare_config.sh $(NAME) $(KEY)

clean: ## Очистити тимчасові файли
	@echo "🧹 Очищення..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name "*.retry" -delete
	@rm -rf tmp/

clean-all: clean ## Очистити все включно з venv
	@echo "🧹 Повне очищення..."
	@rm -rf $(VENV)
	@rm -rf client_keys/*
	@rm -rf generated_configs/*

dirs: ## Створити необхідні директорії
	@mkdir -p client_keys generated_configs logs tmp
