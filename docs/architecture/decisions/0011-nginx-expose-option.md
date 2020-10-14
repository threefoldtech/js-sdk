# 11. Nginx expose option

Date: 2020-10-07

## Status

Accepted

## Context

Minio solution listens for HTTP only. To safely expose it and use it for backups with restic for example, it needs to use HTTPS and use a valid certifcate.

## Decision

Add option to solution expose chatflow to expose solutions using nginx reverse proxy to terminate ssl connections.

## Consequences

Now it is easier for users to expose their apps with https support.
