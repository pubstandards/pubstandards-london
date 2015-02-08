run:
	./env/bin/python ps.py

init:
	rm -rf ./env
	virtualenv ./env

reqs:
	./env/bin/python ./env/bin/pip install -r ./requirements.txt

test:
	./env/bin/flake8 --ignore=E302,E303,E221,E241,E265,E501,E201,E202,W391 ps_data.py ps.py tests
	./env/bin/nosetests

stricttest:
	./env/bin/flake8 --ignore=E302,E221,E241 ps_data.py ps.py tests
	./env/bin/nosetests

