# 10. Update 3bot deployer image to use ubuntu 20.04

Date: 2020-10-04

## Status

Accepted

## Context

Ubuntu 19.10 has become deprecated and poetry version is old which causes poetry failures in 3Bot deployer after removing poetry update and sticking to peotry install using lockfile

## Decision

Update base image (phusion) to use ubuntu 20.04 instead of ubuntu 19.10 and use it in 3Bot deployer

## Consequences

poetry install works with the lockfile and 3Bot deployments are OK
