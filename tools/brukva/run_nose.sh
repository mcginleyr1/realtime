#!/usr/bin/env sh
PYTHONPATH=../facebook-tornado/:. nosetests -w tests $1 --with-coverage --cover-package=brukva --nologcapture --nocapture -v

