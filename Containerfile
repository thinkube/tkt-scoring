# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# The scoring service. Its tests run before this build, in the platform
# pipeline's test step (thinkube.yaml spec.containers[].test); a failing test
# stops the build there.

ARG CONTAINER_REGISTRY

FROM ${CONTAINER_REGISTRY}/library/python-base:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /srv
COPY requirements.txt /srv/requirements.txt
RUN pip install --no-cache-dir -r /srv/requirements.txt
COPY app /srv/app
RUN useradd -m -u 1001 scoring
USER scoring
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
