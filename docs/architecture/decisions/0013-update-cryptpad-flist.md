# 13. Update cryptpad flist

Date: 2020-10-05

## Status

Accepted

## Context

Cryptpad solution image used in docker was deprecated and flist doesn't make use of volumes

## Decision

- Update flist to make use of volumes
- Update base image in docker file to be able to maintain

## Consequences

- Cryptpad solution flist was updated to make use of volumes and s3 backups
