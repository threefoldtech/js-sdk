# 9. add logs in trc and nginx container

Date: 2020-10-01

## Status

Accepted

## Context

Add feature to stream logs from trc and nginx container for better debugging

## Decision

Update the nginx and trc flists to use zinit and redirect logs to stdout to be streamed from redis

## Consequences

Flists were updated and Logs can be streamed for better debugging
