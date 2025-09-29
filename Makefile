install:
	poetry install --no-root


alembic-revision:
	poetry run alembic -c backend/alembic.ini revision --autogenerate -m "init tables"

alembic-upgrade:
	poetry run alembic -c backend/alembic.ini upgrade head

alembic-current:
	poetry run alembic -c backend/alembic.ini current

pre-commit:
	poetry run pre-commit run --all-files


rev: alembic-revision
up: alembic-upgrade
curr: alembic-current
