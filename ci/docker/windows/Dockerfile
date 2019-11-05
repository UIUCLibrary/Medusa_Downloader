# escape=`
ARG PYTHON_VERSION=3.7
FROM python:${PYTHON_VERSION}
RUN certutil -generateSSTFromWU roots.sst ; certutil -addstore -f root roots.sst ; del roots.sst
ENV PIP_DOWNLOAD_CACHE=c:\pip_cache

RUN python -m pip install pip --upgrade ; `
    pip install tox pytest pytest-cov lxml mypy flake8 sphinx wheel requests

