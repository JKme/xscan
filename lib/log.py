#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from settings import ROOT_DIR
from logging.handlers import TimedRotatingFileHandler


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


# Formatter
formatter = logging.Formatter(fmt='%(asctime)s %(filename)s [%(levelname)s] [%(funcName)s] LINE:%(lineno)d %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
log.addHandler(console)
#  FileHandler
infoHandler = TimedRotatingFileHandler(ROOT_DIR + '/logs/info.log', 'D', 1, 7)
infoHandler.setLevel(logging.INFO)
infoHandler.suffix = "%Y-%m-%d.log"
infoHandler.setFormatter(formatter)


errHandler = TimedRotatingFileHandler(ROOT_DIR + '/logs/error.log', 'D', 1, 7)
errHandler.setLevel(logging.ERROR)
errHandler.suffix = "%Y-%m-%d.log"
errHandler.setFormatter(formatter)

log.addHandler(infoHandler)
log.addHandler(errHandler)