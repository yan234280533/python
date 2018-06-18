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

def delete_job_namespace(client,name,namespace):
    try:
       return client.delete_namespaced_job( name=name, body={}, namespace=namespace)
    except Exception as err:
        print("delete_job_namespace failed,%s"%(err))
        return False

def delete_pod_namespace(client,name,namespace):
    try:
        return client.delete_namespaced_pod(name=name, body={}, namespace=namespace)
    except Exception as err:
        print("delete_pod_namespace failed,%s" % (err))
        return False

def get_job_namespace(client,name,namespace):
    try:
       return client.read_namespaced_job( name=name, namespace=namespace)
    except Exception as err:
        print("delete_job_namespace failed,%s"%(err))
        return None
def list_pod_namespace(client,namespace,label_selector):
    try:
       return client.list_namespaced_pod(namespace=namespace,label_selector=label_selector)
    except Exception as err:
        print("list_pod_namespace failed,%s"%(err))
        return None


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    v1Batch = client.BatchV1Api()
    v1Core = client.CoreV1Api()
    count = 100000
    w = watch.Watch()
    for event in w.stream(v1Batch.list_job_for_all_namespaces, timeout_seconds=0):
        try:
            print("Event: %s %s %s" % (
            event['type'], event['object'].metadata.name, event['object'].metadata.namespace))

            if (event['type'] == "ADDED") or (event['type'] == "MODIFIED"):
                object = event['object']
                if object.status.succeeded != None and object.status.succeeded >=1 :
                    if   object.spec.completions != None and  object.spec.completions ==  object.status.succeeded :

                        #判断job的uid是否为空，为空则跳过处理步骤
                        if   object.metadata.uid == None or  object.metadata.uid == "":
                            print("job %s %s uid is null, skip",object.metadata.name,object.metadata.namespace)
                            continue

                        #查找Job对应的Pod，如果所有Pod的状态都为Succeed，则删除所有Pod，否则跳过Job的操作步骤
                        label_selector = "controller-uid=" + object.metadata.uid
                        pods = list_pod_namespace(v1Core,object.metadata.namespace,label_selector)

                        #print("pods: %s " % (pods.to_dict()))

                        if pods != None :
                            for item in pods.items:
                                if item.status.phase == "Succeeded":
                                    ret = delete_pod_namespace(v1Core, item.metadata.name,
                                                               item.metadata.namespace)
                                    if ret:
                                        print("Pod %s %s is deleted" % (
                                            item.metadata.name, item.metadata.namespace))
                                    else:
                                        print("Pod %s %s delete failed" % (
                                            item.metadata.name, item.metadata.namespace))
                                else :
                                    print("job %s %s 's pod %s is Succeeded, skip", object.metadata.name,
                                          object.metadata.namespace,item.metadata.name)
                                    continue

                        # 删除完Pod后，对Job进行删除
                        ret = delete_job_namespace(v1Batch, object.metadata.name,object.metadata.namespace)
                        if ret:
                            print("Job %s %s is deleted" % (
                                object.metadata.name, object.metadata.namespace))
                        else:
                            print("Job %s %s delete failed" % (object.metadata.name, object.metadata.namespace))
            continue
        except Exception as err:
            print("event watch process error,%s" % (err))
            logging.exception(err)
            pass
    w.stop()
    print("Ended.")


if __name__ == '__main__':
    main()