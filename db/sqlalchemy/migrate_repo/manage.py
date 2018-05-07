#!/usr/bin/env python
# -*- coding: utf-8 -*-

from migrate.versioning.shell import main

# This should probably be a console script entry point.
if __name__ == '__main__':
    main(debug='False', repository='.')
