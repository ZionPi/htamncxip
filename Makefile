# 项目名称
PROJECT_NAME := htamncxip
# Conda 环境名称
CONDA_ENV := htamncxip-env
# Python 版本 (锁定 3.10 以兼容 PyTorch/Paddle)
PYTHON_VERSION := 3.10
# 前端/后端端口
PORT_FRONTEND := 8127
PORT_BACKEND := 8128

# Shell 设置
SHELL := /bin/bash

.PHONY: help
help: ## 显示此帮助信息
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: init-project
init-project: ## 初始化项目目录结构
	mkdir -p backend frontend
	touch backend/requirements.txt
	touch README.md FAQ.md LICENSE
	@echo "# $(PROJECT_NAME)" > README.md
	@echo "Project initialized."

.PHONY: create-env
create-env: ## 创建后端 Conda 环境 (Python 3.10)
	conda create -n $(CONDA_ENV) python=$(PYTHON_VERSION) -y
	@echo "Conda environment $(CONDA_ENV) created."

.PHONY: install-backend-deps
install-backend-deps: ## [本地] 安装后端依赖 (需先激活环境)
	@echo "Please run: 'conda activate $(CONDA_ENV)' first, then run 'pip install -r backend/requirements.txt'"

.PHONY: init-frontend
init-frontend: ## 初始化 Electron 前端 (使用 Vite + Vue/React)
	@echo "Initializing frontend with Vite..."
	cd frontend && pnpm create vite . --template vue-ts
	@echo "Installing Electron dependencies..."
	cd frontend && pnpm add -D electron electron-builder vite-plugin-electron vite-plugin-electron-renderer
	cd frontend && pnpm install
	@echo "Frontend initialized."

.PHONY: clean
clean: ## 清理临时文件
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +

.PHONY: info
info: ## 显示项目配置信息
	@echo "Project: $(PROJECT_NAME)"
	@echo "Backend Port: $(PORT_BACKEND)"
	@echo "Frontend Port: $(PORT_FRONTEND)"
	@echo "Conda Env: $(CONDA_ENV)"