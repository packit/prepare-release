FROM quay.io/packit/packit:latest

COPY scripts/ /scripts/

RUN git config --system --add safe.directory /github/workspace

ENTRYPOINT ["/scripts/prepare_release.py"]
