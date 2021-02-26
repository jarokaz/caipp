# Lint as: python2, python3
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""AI Platform Pipelines runner configuration"""

from absl import app
from absl import flags
from absl import logging

from aiplatform.pipelines import client
 
      

FLAGS = flags.FLAGS
flags.DEFINE_integer('train_steps', 100, 'Training steps')
flags.DEFINE_integer('eval_steps', 100, 'Evaluation steps')
flags.DEFINE_string('data_root_uri', 'gs://workshop-datasets/covertype/full', 'Data root')
flags.DEFINE_string('pipeline_root', 'gs://techsummit-bucket/covertype-classifier-pipeline', 'Pipeline root')
flags.DEFINE_string('project_id', 'jk-mlops-dev', 'Project ID')
flags.DEFINE_string('region', 'us-central1', 'Region')
flags.DEFINE_string('api_key', 'None', 'API Key')
flags.DEFINE_string('pipeline_spec_path', 'pipeline.json', 'Pipeline spec path')

def main(argv):
    del argv

    logging.set_verbosity(logging.INFO)

    # Submit the pipeline run
    caipp_client = client.Client(
        project_id=FLAGS.project_id,
        region=FLAGS.region,
        api_key=FLAGS.api_key
    )

    # Set runtime parameters
    pipeline_params = {
        #'train_steps': FLAGS.train_steps,
        #'eval_steps': FLAGS.eval_steps,
        'data_root_uri': FLAGS.data_root_uri,
    }

    # Submit pipeline job
    caipp_client.create_run_from_job_spec(
        job_spec_path=FLAGS.pipeline_spec_path,
        pipeline_root=FLAGS.pipeline_root,
        parameter_values=pipeline_params
    )

if __name__ == '__main__':
    app.run(main)

 