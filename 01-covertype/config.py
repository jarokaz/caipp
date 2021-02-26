# Copyright 2021 Google LLC. All Rights Reserved.
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
"""Compile time parameters.
"""

import os

"""Sets configuration vars."""
# Lab user environment resource settings
GCP_REGION=os.getenv("GCP_REGION", "us-central1")
PROJECT_ID=os.getenv("PROJECT_ID", "dougkelly-sandbox")
CUSTOM_SERVICE_ACCOUNT=os.getenv("CUSTOM_SERVICE_ACCOUNT", "tfx-tuner-caip-service-account@dougkelly-sandbox.iam.gserviceaccount.com")    
# Lab user runtime environment settings
PIPELINE_NAME=os.getenv("PIPELINE_NAME", "covertype-continuous-training")
MODEL_NAME=os.getenv("MODEL_NAME", "covertype_classifier")  
PIPELINE_IMAGE=os.getenv("PIPELINE_IMAGE", "gcr.io/jk-mlops-dev/covertype-tfx")
RUNTIME_VERSION=os.getenv("RUNTIME_VERSION", "2.4")
PYTHON_VERSION=os.getenv("PYTHON_VERSION", "3.7")    
ENABLE_TUNING=os.getenv("ENABLE_TUNING", "True") 
SQL_LITE_PATH=os.getenv("SQL_LITE_PATH", "/tmp/pipeline_root/metadata.sqlite")
DEFAULT_TRAIN_STEPS=os.getenv("DEFAULT_TRAIN_STEPS", 10)
DEFAULT_EVAL_STEPS=os.getenv("DEFAULT_EVAL_STEPS", 10)
DEFAULT_DATA_ROOT=os.getenv("DEFAULT_DATA_ROOT", "gs://workshop-datasets/covertype/small")
    
    