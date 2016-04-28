#encoding: utf-8
# @Author: jeffrey
# @Date:   2016-04-28T19:03:44+08:00
# @Last modified by:   jeffrey
# @Last modified time: 2016-04-28T20:56:39+08:00

import os
import sys


if __name__ =='__main__':
    import dispy
    cluster=dispy.JobCluster()
    jobs=[]
    for i in range(10):
        job=cluster.submit('cat unittest/pcweb_pv.log|python luncher.py pcweb_pv 201604281859',nodes=['172.31.23.211','172.31.21.135'])
        job.id=i
        jobs.append(job)

    for job in jobs:
        host,n=job()
        print('%s executed job %s at %s with %s' % (host, job.id, job.start_time, n))
    cluster.print_status()
