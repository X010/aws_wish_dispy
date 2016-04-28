#encoding: utf-8
# @Author: jeffrey
# @Date:   2016-04-28T19:03:44+08:00
# @Last modified by:   jeffrey
# @Last modified time: 2016-04-28T22:13:54+08:00

#!/usr/bin/env python
import dispy
cluster = dispy.JobCluster('cat unittest/pcweb_pv.log|python luncher.py pcweb_pv 201604281859',nodes=['172.31.23.211','172.31.21.135'])

if __name__ =='__main__':
    import dispy
    import os
    import sys
    cluster=dispy.JobCluster()
    cluster.print_status()
