# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import path

import yaml

from kubernetes import client, config

def delete_job_namespace(client,name,namespace):
    try:
       return client.delete_namespaced_job( name=name, body={}, namespace=namespace)
    except Exception as err:
        print("delete_job_namespace failed,%s"%(err))
        return False

def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    with open(path.join(path.dirname(__file__), "job1.yaml")) as f:
        dep = yaml.load(f)

        print("dep: %s " % (dep))

        v1Batch = client.BatchV1Api()

        for idx2 in range(1, 1000):
            name = "u" + '%06d' % idx2;
            dep['metadata']['name'] = name;
            delete_job_namespace(v1Batch, name, dep['metadata']['namespace']) ;
            print("Job %s deleted" % (name))  ;

        for idx in range(1, 1000) :
            name = "u" + '%06d' % idx;
            dep['metadata']['name'] = name;
            resp = v1Batch.create_namespaced_job(body=dep, namespace=dep['metadata']['namespace'])
            print("Job %s created. status='%s'" % (name,str(resp.status)))

if __name__ == '__main__':
    main()