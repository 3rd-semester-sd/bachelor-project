lint:
	uv run ruff check . --fix
	uv run mypy .


test:
	kubectl exec $$(kubectl get pods | grep booking-service | awk {'print $$1'} | head -n 1) -- pytest ./app/tests -v
