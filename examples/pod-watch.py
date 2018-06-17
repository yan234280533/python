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

def delete_job_namespace(client,name,namespace):
    try:
       return client.delete_namespaced_job( name=name, body={}, namespace=namespace)
    except Exception as err:
        print("delete_job_namespace failed,%s"%(err))
        return False
    finally:
        print("delete_job_namespace failed,no exception")
        return False


def delete_pod_namespace(client,name,namespace):
    try:
        return client.delete_namespaced_pod(name=name, body={}, namespace=namespace)
    except Exception as err:
        print("delete_pod_namespace failed,%s" % (err))
        return False
    finally:
        print("delete_pod_namespace failed,no exception")
        return False

def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    v1 = client.CoreV1Api()
    count = 100000
    w = watch.Watch()
    for event in w.stream(v1.list_pod_for_all_namespaces, timeout_seconds=0):
        print("Event: %s %s %s %s" % (event['type'], event['object'].metadata.name,event['object'].metadata.namespace,event['object'].status.phase))
        #print("Dict: %s " % (event['object'].to_dict()))
        if (event['type'] == "ADDED") or (event['type'] == "MODIFIED"):
            if event['object'].status.phase == "Succeeded":
                #如果Pod的状态为“Succeed“时，删除Pod
                print("Pod %s %s is run succeed" % (event['object'].metadata.name, event['object'].metadata.namespace))
                ret = delete_pod_namespace(v1, event['object'].metadata.name, event['object'].metadata.namespace)
                if ret:
                    print("Pod %s %s is deleted" % (
                        event['object'].metadata.name, event['object'].metadata.namespace))
                else:
                    print("Pod %s %s delete failed" % (
                        event['object'].metadata.name, event['object'].metadata.namespace))

                #如果能够查找到Pod属于哪个Job，则对应的删除Job
                if  event['object'].metadata.owner_references != None and event['object'].metadata.owner_references[0].kind == "Job":
                    ret = delete_job_namespace(client.BatchV1Api(),event['object'].metadata.owner_references[0].name,event['object'].metadata.namespace)
                    if ret:
                        print("Job %s %s is deleted" % (
                            event['object'].metadata.owner_references[0].name, event['object'].metadata.namespace))
                    else:
                        print("Job %s %s delete failed" % (
                            event['object'].metadata.owner_references[0].name, event['object'].metadata.namespace))
            count += 1
        count += 1
        if not count:
            w.stop()

    print("Ended.")


if __name__ == '__main__':
    main()
