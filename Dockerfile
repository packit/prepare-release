FROM quay.io/packit/packit:latest

COPY scripts/ /scripts/

ENTRYPOINT ["/scripts/prepare_release.py"]
