#!/usr/bin/thrift --gen py:twisted

# Copyright (C) 2005-2010  MISG/ICTI/EIA-FR
# See LICENSE for details.

namespace py smac.api.models


exception ValidationError {
    1: string message
}

exception DoesNotExist {
    1: string query
}