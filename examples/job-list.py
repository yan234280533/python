#!/usr/bin/python
#-*- coding:utf-8 -*-

# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from kubernetes import client, config, watch
import logging
import time
import sys

def delete_job_namespace(client,name,namespace):
    try:
       return client.delete_namespaced_job( name=name, body={}, namespace=namespace)
    except Exception as err:
        logger.info("delete_job_namespace failed,%s"%(err))
        return False

def delete_pod_namespace(client,name,namespace):
    try:
        return client.delete_namespaced_pod(name=name, body={}, namespace=namespace)
    except Exception as err:
        logger.info("delete_pod_namespace failed,%s" % (err))
        return False

def get_job_namespace(client,name,namespace):
    try:
       return client.read_namespaced_job( name=name, namespace=namespace)
    except Exception as err:
        logger.info("delete_job_namespace failed,%s"%(err))
        return None

def list_pod_namespace(client,namespace,label_selector):
    try:
       return client.list_namespaced_pod(namespace=namespace,label_selector=label_selector)
    except Exception as err:
        logger.info("list_pod_namespace failed,%s"%(err))
        return None


def main():
    # 创建一个logger
    logger = logging.getLogger('mytest111')
    logger.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(message)s")    # output format
    sh = logging.StreamHandler(stream=sys.stdout)    # output to standard output
    sh.setFormatter(format)
    logger.addHandler(sh)

    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    v1Batch = client.BatchV1Api()
    v1Core = client.CoreV1Api()

    print("begin print")
    logger.setLevel(logging.DEBUG)
    logger.info("begin info")
    logger.error("begin error")

    while 1:
       time.sleep(1)  # 休眠1秒
       try:
           jobs = v1Batch.list_job_for_all_namespaces(watch=False)
           for object in jobs.items:
               if object.status.succeeded != None and object.status.succeeded >= 1:
                   if object.spec.completions != None and object.spec.completions == object.status.succeeded:
                       ret = delete_job_namespace(v1Batch, object.metadata.name, object.metadata.namespace)
                       if ret:
                           logger.info("Job %s %s is deleted" % (
                               object.metadata.name, object.metadata.namespace))
                       else:
                           logger.info("Job %s %s delete failed" % (object.metadata.name, object.metadata.namespace))

           #拉取所有的pod，如果pod为完成状态，并且pod无owner_references，则删除
           pods = v1Core.list_pod_for_all_namespaces(watch=False)
           for object in pods.items:
                if object.status.phase == "Succeeded":
                    if object.metadata.owner_references == None :
                        ret = delete_pod_namespace(v1Core, object.metadata.name, object.metadata.namespace)
                        if ret:
                            logger.info("Pod %s %s is deleted" % (object.metadata.name, object.metadata.namespace))
                        else:
                            logger.info("Pod %s %s delete failed" % (object.metadata.name, object.metadata.namespace))

       except Exception as err:
           logger.info("event watch process error,%s" % (err))
           logger.exception(err)
           pass

    logger.info("Ended.")

if __name__ == '__main__':
    main()