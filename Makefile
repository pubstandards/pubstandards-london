ifeq ("$(VIRTUAL_ENV)", "")
  ENV=. ./env/bin/activate;
endif

run:
	$(ENV) python ps.py

init:
	rm -rf ./env
	virtualenv -p python2.7 ./env

reqs:
	$(ENV) pip install -r ./requirements.txt

test:
	$(ENV) flake8 --ignore=E302,E303,E221,E241,E265,E501,E201,E202,W391 ps_data.py ps.py tests
	$(ENV) nosetests

stricttest:
	$(ENV) flake8 --ignore=E302,E221,E241 ps_data.py ps.py tests
	$(ENV) nosetests

