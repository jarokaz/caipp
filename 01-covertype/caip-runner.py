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
from tfx.orchestration.kubeflow.v2 import kubeflow_v2_dag_runner

import config
import pipeline 

PIPELINE_SPEC_PATH = 'pipeline.json'

  # Set the values for the compile time parameters
_ai_platform_training_args = {
    'project': config.PROJECT_ID,
    'region': config.GCP_REGION,
    'serviceAccount': config.CUSTOM_SERVICE_ACCOUNT,
    'masterConfig': {
        'imageUri': config.PIPELINE_IMAGE,
    }
}

# Pipeline arguments for Beam powered Components.
_beam_pipeline_args = [
    '--direct_running_mode=multi_processing',
    # 0 means auto-detect based on on the number of CPUs available
    # during execution time.
    '--direct_num_workers=0',
]

FLAGS = flags.FLAGS
flags.DEFINE_integer('train_steps', 100, 'Training steps')
flags.DEFINE_integer('eval_steps', 100, 'Evaluation steps')
flags.DEFINE_string('pipeline_root', 'gs://techsummit-bucket/covertype-classifier-pipeline', 'Pipeline root')
flags.DEFINE_string('pipeline_name', 'covertype-classifier-pipeline', 'Pipeline name')
flags.DEFINE_string('project_id', 'jk-mlops-dev', 'Project ID')
flags.DEFINE_string('region', 'us-central1', 'Region')
flags.DEFINE_string('api_key', 'None', 'API Key')

def main(argv):
    del argv

    logging.set_verbosity(logging.INFO)

    # Create pipeline
    pipeline_def = pipeline.create_pipeline(
        pipeline_name=FLAGS.pipeline_name,
        pipeline_root=FLAGS.pipeline_root,
        data_root_uri=config.DATA_ROOT_URI,
        train_steps=FLAGS.train_steps,
        eval_steps=FLAGS.eval_steps,
        beam_pipeline_args=_beam_pipeline_args)

    # Create Kubeflow V2 runner
    runner_config = kubeflow_v2_dag_runner.KubeflowV2DagRunnerConfig(
        project_id=FLAGS.project_id,
        display_name=FLAGS.pipeline_name,
        default_image=config.PIPELINE_IMAGE)

    runner = kubeflow_v2_dag_runner.KubeflowV2DagRunner(
        config=runner_config,
        output_filename=PIPELINE_SPEC_PATH)

    # Compile the pipeline
    runner.compile(pipeline_def)

    return

    # Submit the pipeline run
    caipp_client = client.Client(
        project_id=FLAGS.project_id,
        region=FLAGS.region,
        api_key=FLAGS.api_key
    )

    caipp_client.create_run_from_job_spec(
        job_spec_path=PIPELINE_SPEC_PATH
    )

if __name__ == '__main__':
    app.run(main)

 