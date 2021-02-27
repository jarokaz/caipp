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
"""Local runner configuration"""

from absl import app
from absl import flags
from absl import logging

from tfx.dsl.components.base import executor_spec
from tfx.components.trainer import executor as trainer_executor
from tfx.extensions.google_cloud_ai_platform.trainer import executor as ai_platform_trainer_executor

from tfx.orchestration import data_types
from tfx.orchestration.local.local_dag_runner import LocalDagRunner
from tfx.orchestration.metadata import sqlite_metadata_connection_config

import config
import pipeline 

# Pipeline arguments for Beam powered Components.
_beam_pipeline_args = [
    '--direct_running_mode=multi_processing',
    # 0 means auto-detect based on on the number of CPUs available
    # during execution time.
    '--direct_num_workers=0',
]

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

FLAGS = flags.FLAGS
flags.DEFINE_integer('train_steps', 100, 'Training steps')
flags.DEFINE_integer('eval_steps', 100, 'Evaluation steps')
flags.DEFINE_string('data_root_uri', 'gs://workshop-datasets/covertype/small', 'Data root')

def main(argv):
    del argv

    logging.set_verbosity(logging.INFO)
    pipeline_def = pipeline.create_pipeline(
        pipeline_name=config.PIPELINE_NAME,
        pipeline_root=config.DEFAULT_PIPELINE_ROOT,
        data_root_uri=FLAGS.data_root_uri,
        eval_steps=FLAGS.eval_steps,
        train_steps=FLAGS.train_steps,
        custom_executor_spec=_custom_executor_spec,
        custom_config=_custom_config,
        beam_pipeline_args=_beam_pipeline_args)

    LocalDagRunner().run(pipeline_def)

if __name__ == '__main__':
    app.run(main)

 



