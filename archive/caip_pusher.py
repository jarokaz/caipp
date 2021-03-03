# Copyright 2021 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Custom TFX component that uploads the model to Cloud AI Platform Models."""


import logging

from google.cloud import aiplatform

from tfx.dsl.component.experimental.decorators import component
from tfx.dsl.component.experimental.annotations import InputArtifact, OutputArtifact, Parameter, OutputDict

from tfx.types.standard_artifacts import Model

@component
def upload_model(
    project_id: Parameter[str],
    display_name: Parameter[str],
    serving_container: Parameter[str],
    region: Parameter[str],
    model: InputArtifact[Model]) -> OutputDict(model_name=str):
    """Uploads model artifacts to AI Platform Models."""

    api_endpoint = f'{region}-aiplatform.googleapis.com'
    parent = f'projects/{project_id}/locations/{region}'

    client_options = {'api_endpoint': api_endpoint}
    client = aiplatform.gapic.ModelServiceClient(client_options=client_options)

    artifact_uri = '{}/serving_model_dir'.format(model.uri)
    model_spec = {
        'display_name': display_name,
        'metadata_schema_uri': "",
        'artifact_uri': artifact_uri,
        'container_spec': {
            'image_uri': serving_container,
            'command': [],
            'args': []
        }
    }

    response = client.upload_model(parent=parent, model=model_spec)
    logging.info('Uploading model {}. Operation ID: {}'.format(model, response.operation.name))
    upload_model_response = response.result()
    logging.info('Upload completed.')
    
    return {'model_name': upload_model_response}
