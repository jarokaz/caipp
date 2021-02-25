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

from tfx.orchestration import data_types
from tfx.orchestration.local.local_dag_runner import LocalDagRunner
from tfx.orchestration.metadata import sqlite_metadata_connection_config

import config
import pipeline 


  # Set the values for the compile time parameters
_ai_platform_training_args = {
    'project': config.PROJECT_ID,
    'region': config.GCP_REGION,
    'serviceAccount': config.CUSTOM_SERVICE_ACCOUNT,
    'masterConfig': {
        'imageUri': config.TFX_IMAGE,
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
flags.DEFINE_string('pipeline_root', '/tmp/pipeline_root', 'Pipeline root')
flags.DEFINE_string('pipeline_name', 'covertype_classifier_pipeline', 'Pipeline name')

def main(argv):
    del argv

    logging.set_verbosity(logging.INFO)
    pipeline_def = pipeline.create_pipeline(
        pipeline_name=FLAGS.pipeline_name,
        pipeline_root=FLAGS.pipeline_root,
        data_root_uri=config.DATA_ROOT_URI,
        train_steps=FLAGS.train_steps,
        eval_steps=FLAGS.eval_steps,
        beam_pipeline_args=_beam_pipeline_args)

    print('*****')
    print(pipeline_def)
    LocalDagRunner().run(pipeline_def)

if __name__ == '__main__':
    app.run(main)

 



