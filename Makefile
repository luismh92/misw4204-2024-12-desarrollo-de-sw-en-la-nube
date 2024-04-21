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

i-nfs:
	sudo apt-get install nfs-kernel-server

make-dir:
	sudo mkdir -p /var/nfs_share

nfs-group:
	sudo chown nobody:nogroup /var/nfs_share

nfs-export:
	sudo /etc/exports

compose-be-up:
	docker-compose -f compose.gcp-backend.yaml up

compose-worker-up:
	docker-compose -f compose.gcp-worker.yaml up


# /var/nfs_share 192.168.128.0/24(rw,sync,no_subtree_check)