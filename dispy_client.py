#encoding: utf-8
# @Author: jeffrey
# @Date:   2016-04-28T19:03:44+08:00
# @Last modified by:   jeffrey
# @Last modified time: 2016-04-28T23:02:21+08:00


def compute(filepath):
    import socket
    import os
    import commands
    host = socket.gethostname()
    status,output=commands.getstatusoutput('aws s3 cp '+filepath+' /home/ec2-user/')
    return (host, output)

if __name__ =='__main__':
    import dispy, random
    cluster = dispy.JobCluster(compute,nodes=['172.31.23.211','172.31.21.135'])

    files_dict=["s3://x010/iphone/pv/access_2016-04-14-14-45.log","s3://x010/iphone/pv/access_2016-04-14-14-40.log","s3://x010/iphone/pv/access_2016-04-14-14-35.log","s3://x010/iphone/pv/access_2016-04-14-14-35.log"]
    jobs = []
    i=0
    for val in files_dict:
        job=cluster.submit(val)
        job.id=i
        i+=1

        jobs.append(job)

    for job in jobs:
        host,n=job()
        print('%s executed job %s at %s with %s' % (host, job.id, job.start_time, n))
    cluster.print_status()
