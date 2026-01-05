VENV=.venv

.PHONY: install-kivy run-kivy run-kivy-reqs

install-kivy:
	python -m pip install --upgrade pip
	pip install -r apps/delphia/kivy/requirements.txt

run-kivy: install-kivy
	python apps/delphia/kivy/main.py

run-kivy-reqs:
	python -m pip install -r apps/delphia/kivy/requirements.txt
