#encoding: utf-8
# @Author: jeffrey
# @Date:   2016-04-28T18:18:24+08:00
# @Last modified by:   jeffrey
# @Last modified time: 2016-04-28T18:21:33+08:00

import ConfigParser
import os

ServerConf = ConfigParser.ConfigParser()
ServerConf.read(os.path.join(os.path.dirname(__file__), "../etc/service.conf"))
