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

from tfx.components.trainer import executor as trainer_executor
from tfx.extensions.google_cloud_ai_platform.trainer import executor as ai_platform_trainer_executor

from tfx.orchestration import data_types
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

_custom_config = {
    ai_platform_trainer_executor.TRAINING_ARGS_KEY: _ai_platform_training_args
}
_custom_executor_spec=executor_spec.ExecutorClassSpec(ai_platform_trainer_executor.GenericExecutor)

_custom_executor_spec=executor_spec.ExecutorClassSpec(trainer_executor.GenericExecutor)
_custom_config = None


# Pipeline arguments for Beam powered Components.
_beam_pipeline_args = [
    '--direct_running_mode=multi_processing',
    # 0 means auto-detect based on on the number of CPUs available
    # during execution time.
    '--direct_num_workers=0',
]

# Define runtime parameters
_train_steps = data_types.RuntimeParameter(
    name='train_steps',
    ptype=int,
    default=config.DEFAULT_TRAIN_STEPS
  )

_eval_steps = data_types.RuntimeParameter(
    name='eval_steps',
    ptype=int,
    default=config.DEFAULT_EVAL_STEPS
  )

_data_root_uri = data_types.RuntimeParameter( 
      name='data_root_uri',
      ptype=str,
      default=config.DEFAULT_DATA_ROOT)
      
FLAGS = flags.FLAGS
flags.DEFINE_string('pipeline_spec_path', 'pipeline.json', 'Pipeline spec path')
flags.DEFINE_string('project_id', 'jk-mlops-dev', 'Project ID')

def main(argv):
    del argv

    # Create pipeline
    pipeline_def = pipeline.create_pipeline(
        pipeline_name=config.PIPELINE_NAME,
        pipeline_root=config.DEFAULT_PIPELINE_ROOT,
        data_root_uri=_data_root_uri,
        train_steps=_train_steps,
        eval_steps=_eval_steps,
        executor_spec=_custom_executor_spec,
        custom_config=_custom_config,
        beam_pipeline_args=_beam_pipeline_args)

    # Create Kubeflow V2 runner
    runner_config = kubeflow_v2_dag_runner.KubeflowV2DagRunnerConfig(
        project_id=FLAGS.project_id,
        display_name=config.PIPELINE_NAME,
        default_image=config.PIPELINE_IMAGE)

    runner = kubeflow_v2_dag_runner.KubeflowV2DagRunner(
        config=runner_config,
        output_filename=FLAGS.pipeline_spec_path)

    # Compile the pipeline
    runner.run(pipeline_def)

if __name__ == '__main__':
    app.run(main)

 