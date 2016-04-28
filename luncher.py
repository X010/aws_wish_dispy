#encoding: utf-8
# @Author: jeffrey
# @Date:   2016-04-28T17:34:42+08:00
# @Last modified by:   jeffrey
# @Last modified time: 2016-04-28T22:23:05+08:00

import os
import sys
from util.pydotalog import pydotalog
from parsing.format_pcweb_pv import PcWebPvFormat

topic_class_dict={
        'pcweb_pv': PcWebPvFormat
}

def get_class_name(topic_name, start_time):
    if topic_name not in topic_class_dict.keys():
        return (-1, 'topic : %s format class not found' % topic_name)
    return (0, topic_class_dict.get(topic_name)(start_time, topic_name))


def process_main():
    for line in sys.stdin:
        format_client.processFormat(line)

if __name__ == '__main__':

    log_dir = os.path.join(os.path.dirname(__file__), "./log/")
    pydotalog.init_logger(log_dir + "/pydota_run.log")

    if len(sys.argv) == 3:
        (di, topic_name, start_time) = sys.argv
        (rt, format_client) = get_class_name(topic_name, start_time)


        if rt != 0:
            pydotalog.error(format_client)
            sys.exit(-1)

        print len(start_time)
        if len(start_time) != 12:
            pydotalog.error("topic:[%s] start_time format error, start_time: %s", topic_name, start_time)
            sys.exit(-1)

        process_main()

    else:
        pydotalog.error('arg is topic_name date')
        sys.exit(-1)
