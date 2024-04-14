install:
	pip3 install -r requirements.txt --no-cache --extra-index-url https://pypi.org/simple

run-app:
	uvicorn app.main:app --reload

req-file:
	pip3 freeze > requirements.txt

run-compose:
	docker-compose up -d --build

down-compose:
	docker-compose down

kill:
	kill -9 1454
	kill -9 4907	