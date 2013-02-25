# -*- coding: utf8 -*-

import re

def parse_range_header(range):
    match = re.match('^items=([0-9]+)-([0-9]+)$', range)
    if match:
        start = int(match.group(1))
        finish = int(match.group(2))
        if finish < start:
            finish = start
        return {
            'start': start,
            'finish': finish,
            'number': finish - start + 1
        }
    else:
        return False
