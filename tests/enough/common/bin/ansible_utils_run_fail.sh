#!/bin/bash

echo stdout1
echo stdout2
echo stderr1 >&2
exit 1
