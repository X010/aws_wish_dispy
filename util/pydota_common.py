#encoding: utf-8
# @Author: jeffrey
# @Date:   2016-04-28T19:31:24+08:00
# @Last modified by:   jeffrey
# @Last modified time: 2016-04-28T19:33:46+08:00

import ConfigParser
import sys
import os
import time
import string
from IPy import IP
from util.conf_settings import ServerConf
from util.pydotalog import pydotalog

GEOIP_SORT = []
GEOIP = {}
file_list = {}


def LoadLiveMeizi(start_time):
    """
    :summery: 加载直播媒资信息
    :param start_time: 加载媒资信息的时刻，12为字符串，201511031700
    :return: 媒资信息dict
    """
    Meizi_info = {}

    try:
        output_path = ServerConf.get("meizi", "output_path")
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
        pydotalog.error("initConfig fail:%s", str(e))
        sys.exit(-1)

    file = output_path + '/' + start_time + '_live.csv'
    if not os.path.exists(file):
        pydotalog.error("live_meizi info file is not exists!")
        sys.exit(-1)

    with open(file) as fp:
        for i, line in enumerate(fp):
            try:
                record = line.strip().split(',')
                sourceid = record[0]
                activityid = record[2]
                cameraid = record[5]
                timeid = record[7]
                startTime = record[8]
                endTime = record[9]
                try:
                    Meizi_info[sourceid].append([activityid, cameraid, timeid, startTime, endTime])
                except KeyError:
                    Meizi_info[sourceid] = []
                    Meizi_info[sourceid].append([activityid, cameraid, timeid, startTime, endTime])
            except KeyError:
                pydotalog.error("line[%d]: live meizi index err!", i)
                continue
    return Meizi_info


def CheckLiveTime(log_time, live_info=[]):
    """
    :summery 校验日志时间是否有效的活动时间期间,并返回活动id和活动摄像机id
    :param log_time: 需要校验的日志时间时间戳
    :param live_info: 日志对应活动的活动信息，list数组
    :return: errnum,str,str 0-有效 －1 时间格式错误 －2 时间不在有效期内
    """
    for live_info_one in live_info:
        try:
            startTime = time.strptime(live_info_one[3], "%Y-%m-%d %H:%M:%S")
            endTime = time.strptime(live_info_one[4], "%Y-%m-%d %H:%M:%S")

            startTime = int(time.mktime(startTime))
            endTime = int(time.mktime(endTime))

            if startTime <= int(log_time) <= endTime:
                return 0, live_info_one[0], live_info_one[1]
            else:
                continue

        except (KeyError, ValueError) as e:
            pydotalog.error("check time failed: %s", str(e))
            return -1, 0, 0

    pydotalog.error("%s is not a valid time !", str(log_time))
    return -2, 0, 0


def loadGeoIp(filename):
    """
    :summery: 加载GEOIP库
    :param filename: GEOIP文件路径
    :return: 生成GEOIP相关dict
    """
    fp = open(filename)
    for i, line in enumerate(fp):
        try:
            record = string.split(line, "\t")
            rangmin  = record[0]
            rangmax  = record[1]
            country  = record[2]
            province = record[3]
            city     = record[4]
            operator = record[6]
            rangmin = IP(rangmin).int()
            rangmax = IP(rangmax).int()
            GEOIP[rangmin] = [rangmax, country, province, city, operator]
            GEOIP_SORT.append(rangmin)
        except ValueError:
            sys.stderr.write(("value error,%s") % line)
    GEOIP_SORT.sort()
    fp.close()


def _getRangeKey(userip):
    low = 0
    height = len(GEOIP_SORT)-1
    while low < height:
        mid = (low+height)/2
        if GEOIP_SORT[mid] < userip and GEOIP_SORT[mid + 1] < userip:
            low = mid + 1
        elif GEOIP_SORT[mid] > userip and GEOIP_SORT[mid - 1] > userip:
            height = mid - 1
        elif GEOIP_SORT[mid] <= userip and GEOIP_SORT[mid +1] > userip:
            return GEOIP_SORT[mid]
        elif GEOIP_SORT[mid -1] <= userip and GEOIP_SORT[mid] > userip:
            return GEOIP_SORT[mid -1]
        elif GEOIP_SORT[mid + 1] == userip:
            return GEOIP_SORT[mid +1]
        else:
            return None
    return None


def formatLocation(userip):
    """
    :summery: 根据userip获取地域信息
    :param userip: 用户ip 127.0.0.1
    :return: 地域信息list
    """
    userip = userip.strip('""')
    userip = IP(userip).int()
    location = _getRangeKey(userip)
    if location and GEOIP[location]:
        if location <= userip <= GEOIP[location][0]:
            return GEOIP[location]
    else:
        return None


def formatTime(timedata):
    """
    :summery time结构体格式化时间输出，异常时,抛出ValueError
    :param timedata: time结构体结构
    :return:年月日字符串,时分秒字符串,时间戳
    """
    try:
        timetmp_date = time.strftime('%Y%m%d', timedata)
        timetmp_time = time.strftime('%H%M%S', timedata)
        timeStamp = int(time.mktime(timedata))
        return timetmp_date, timetmp_time, timeStamp
    except (ValueError, TypeError):
        raise ValueError("timeerr")


def __genOutputFileName(log_time, topic, start_time, data_type):
    """
    根据日志时间，topic，后缀，数据类型拼接写入文件
    :param log_time: 需要写入的日志时间,精确到小时
    :type log_time: basestring 201511012200 12位
    :param topic: kafka－topic名称
    :type topic: basestring
    :param start_time: 文件后缀名称, 为recv文件的时刻
    :type start_time: basestring 201511012300 12位
    :param data_type: 写入数据的类型，分为 orig,des,err
    :type data_type: basestring
    :return:
    """
    try:
        output_path = ServerConf.get("output_path", data_type)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
        pydotalog.error("initConfig fail:%s", str(e))
        return ""

    if "err" in data_type:
        file_str = '{0}/{1}/{2}/err_{3}_{4}_{5}'.format(str(output_path), log_time[0:4],
                                                log_time[4:6], log_time, topic, start_time)
    elif "des" == data_type:
        if "_pv" in topic:
            file_str = '{0}/{1}/{2}/{3}_pvrawdata_{4}_{5}'.format(str(output_path), log_time[0:4],
                                                    log_time[4:6], log_time, topic, start_time)
        elif "mglive" in topic:
            file_str = '{0}/{1}/{2}/{3}_mgliverawdata_{4}_{5}'.format(str(output_path), log_time[0:4],
                                                    log_time[4:6], log_time, topic, start_time)
        else:
            file_str = '{0}/{1}/{2}/{3}_playrawdata_{4}_{5}'.format(str(output_path), log_time[0:4],
                                                    log_time[4:6], log_time, topic, start_time)
    else:
        file_str = '{0}/{1}/{2}/{3}_{4}_{5}'.format(str(output_path), log_time[0:4],
                                                log_time[4:6], log_time, topic, start_time)
    file_str = os.path.abspath(file_str)
    dir_name = os.path.dirname(file_str)
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except OSError as e:
            pydotalog.error("make dir failed:[%s]", str(e))
            return ""
    return file_str


def __output_to_files(log_time, line, topic, start_time, data_type):
    str_log_file = __genOutputFileName(log_time, topic, start_time, data_type)

    if str_log_file == "":
        return False

    if str_log_file in file_list:
        log_file = file_list[str_log_file]
    else:
        try:
            log_file = open(str_log_file, 'w')
            file_list[str_log_file] = log_file
        except IOError as e:
            pydotalog.error("IOError: %s", str(e))
            return False

    log_file.write(line.strip('\n') + '\n')
    return True


def __check_time(log_time):
    """
    :summary: 校验log_time是否合理
    :param log_time: 201510101000
    :return: boolean
    """
    if len(log_time) != 12:
        return False
    try:
        return 201000000000 < int(log_time) < 205000000000
    except ValueError:
        pydotalog.error("log_time[%s] is overtime", str(log_time))
        return False


def write_to_file(line, topic, log_time, start_time, data_type):
    """
    :summary: 根据传入时间以及日志时间，写入对应文件
    :param line: 需要写入的数据,分为原始日志数据和清洗后的des
    :type line: basestring
    :param topic: kafka－topic名称
    :type topic: basestring
    :param log_time: 需要写入的日志时间,精确到小时
    :type log_time: basestring 201511012200 12位
    :param start_time: 文件后缀名称, 为recv文件的时刻
    :type start_time: basestring 201511012300 12位
    :param data_type: 写入数据的类型，分为 orig,des,des_err,orig_err
    :type data_type: basestring
    :return: boolean 是否成功写入
    """
    if __check_time(log_time):
        return __output_to_files(log_time, line, topic, start_time, data_type)
    else:
        return False


def check_act_field(line, *args):
    if len(line.strip('\n')) == 0 or len(args) == 0:
        return False
    for arg in args:
        act_str = '"act":"' + str(arg) + '"'
        if line.find(act_str) != -1:
            return True

    return False


def check_pt_field(line, *args):
    if len(line.strip('\n')) == 0 or len(args) == 0:
        return False
    for arg in args:
        act_str = '"pt":"' + str(arg) + '"'
        act_str1 = '"pt":' + str(arg)
        if line.find(act_str) != -1 or line.find(act_str1) != -1:
            return True

    return False


def ip_into_int(ip):
    # 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“.”后转成10进制的 3232235789 即可。
    # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    try:
        ip_int = reduce(lambda x, y: (x << 8)+y, map(int, ip.split('.')))
    except ValueError:
        return 0
    return ip_int


def is_internal_ip(ip):
    ip = ip_into_int(ip)

    # 无效ip统一当内网ip透传
    if ip == 0:
        return True
    net_a = ip_into_int('10.255.255.255') >> 24
    net_b = ip_into_int('172.31.255.255') >> 20
    net_c = ip_into_int('192.168.255.255') >> 16
    return ip >> 24 == net_a or ip >> 20 == net_b or ip >> 16 == net_c


if __name__ == "__main__":
    pass
