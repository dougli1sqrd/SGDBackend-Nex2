.PHONY: test lib config

build:
	npm install
	npm run build
	pip install -r requirements.txt
	python setup.py develop

prod-build:
	pip install -r requirements.txt
	python setup.py develop

run:
	source dev_variables.sh && pserve development.ini --reload

tests:
	npm test
	source test_variables.sh && nosetests -s

qa-index-redis:
	source dev_variables.sh && NEX2_URI=$$QA_NEX2_URI && cap qa deploy:redis

qa-deploy:
	source dev_variables.sh && NEX2_URI=$$QA_NEX2_URI && cap qa deploy

qa-restart:
	source dev_variables.sh && NEX2_URI=$$QA_NEX2_URI && cap qa deploy:restart

curate-deploy:
	npm run build && source dev_variables.sh && NEX2_URI=$$CURATE_NEX2_URI && cap curate_dev deploy

curate-qa-deploy:
	source dev_variables.sh && NEX2_URI=$$CURATE_NEX2_URI && cap curate_qa deploy

deploy:
	npm run build && source dev_variables.sh && cap dev deploy

staging-deploy:
	source prod_variables.sh && cap staging deploy

curate-staging-deploy:
	npm run build && source prod_variables.sh && NEX2_URI=$$CURATE_NEX2_URI && cap curate_staging deploy

prod-deploy:
	npm run build && source prod_variables.sh && cap prod deploy

run-prod:
	pserve production.ini --daemon --pid-file=/var/run/pyramid/backend.pid

stop-prod:
	-pserve production.ini --stop-daemon --pid-file=/var/run/pyramid/backend.pid

lint:
	eslint src/client/js/

refresh-cache:
	source dev_variables.sh && python src/loading/scrapy/pages/spiders/pages_spider.py

refresh-prod-cache:
	source /data/envs/sgd/bin/activate && source prod_variables.sh && python src/loading/scrapy/pages/spiders/pages_spider.py

index-es:
	source dev_variables.sh && python scripts/search/index_elastic_search.py

index-redis:
	source dev_variables.sh && python scripts/disambiguation/create_disambiguation.py

create-disambiguation:
	source dev_variables.sh && python scripts/disambiguation/create_disambiguation.py
