#encoding: utf-8
# @Author: jeffrey
# @Date:   2016-04-28T18:59:54+08:00
# @Last modified by:   jeffrey
# @Last modified time: 2016-04-28T19:01:54+08:00

import sys
import ConfigParser
import fileinput
import urllib
from format_base import FormatBase
from util.conf_settings import ServerConf

class PcWebPvFormat(FormatBase):
    """
    pcweb_pv
    """
    def __init__(self, recv_time, topic_name='pcweb_pv'):
        super(PcWebPvFormat, self).__init__(recv_time)
        self.name = topic_name
        self.log_all_list = []
        try:
            self.des_key_list = eval(ServerConf.get(self.name, "des_key_list"))
            self.des_dict_list = eval(ServerConf.get(self.name, "des_dict_list"))
            self.des_dict = eval(ServerConf.get(self.name, "des_dict"))
        except(ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
            sys.stderr.write("[%s] initConfig fail:%s" % (self.name, str(e)))
            sys.exit(-1)

    def getDictByLog(self, log_str):
        """
        通过日志获取Dict
        :param log_str:
        :return:
        """
        _dict = {}
        res_list = log_str.strip().split('\t')
        if len(res_list) < 8:
            return [-1, "indexerr"]
        url_content = res_list[7]
        res_tmp = self.getDictByUrlNew(url_content, _dict)

        if res_tmp[0] != 0:
            return res_tmp
        _dict['ip'] = res_list[1]
        _dict['time'] = res_list[0]

        return [0, _dict]
