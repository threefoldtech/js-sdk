# 6. packages

Date: 2020-09-13

## Status

Accepted

## Context

Failed to install weblibs package on fresh installation

## Decision

Add pre-install method to packages. This method will have the code that will be executed once before installation and package can't go without and that will seperate using install with kwargs for configuring the package and pre-install to dependancies like git clone.

## Consequences

This will seperate using install with kwargs for configuring the package and pre-install to dependancies like git clone.
