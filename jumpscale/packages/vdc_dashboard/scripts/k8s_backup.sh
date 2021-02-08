#!/bin/bash

RESOURCES=$(kubectl api-resources --namespaced -o name | tr "\n" " ")
for resource in
