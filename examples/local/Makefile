.PHONY: init help

## Show help for all commands
help:
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9._-]+:.*?## / {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build docker containers
	docker-compose build

up: ## Run all the docker containers
	docker-compose up -d
	$(MAKE) logs

down: ## Stop all the docker containers
	docker-compose down

restart: ## Restart all the docker containers
	docker-compose restart

logs: ## Follow all container logs
	docker-compose logs -f

logs-master: ## Follow locust master logs
	docker-compose logs -f locust_master

logs-worker: ## Follow locust worker logs
	docker-compose logs -f locust_worker

locust-bash: ## Get inside locust master container
	docker-compose exec locust_master bash
