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
"""Covertype training pipeline DSL."""

import os
import kfp
import tensorflow_model_analysis as tfma

from absl import app
from absl import flags


from ml_metadata.proto import metadata_store_pb2

from tfx.components import Evaluator
from tfx.components import CsvExampleGen
from tfx.components import ExampleValidator
from tfx.components import ImporterNode
from tfx.components import Pusher
from tfx.components import ResolverNode
from tfx.components import SchemaGen
from tfx.components import StatisticsGen
from tfx.components import Trainer
from tfx.components import Transform
from tfx.components.trainer import executor as trainer_executor
from tfx.dsl.experimental import latest_blessed_model_resolver
from tfx.dsl.components.base import executor_spec
from tfx.extensions.google_cloud_ai_platform.pusher import executor as ai_platform_pusher_executor
from tfx.extensions.google_cloud_ai_platform.trainer import executor as ai_platform_trainer_executor
from tfx.extensions.google_cloud_ai_platform.tuner.component import Tuner
from tfx.orchestration import pipeline
from tfx.orchestration import data_types
from tfx.orchestration.metadata import sqlite_metadata_connection_config
from tfx.orchestration.kubeflow.proto import kubeflow_pb2
from tfx.proto import example_gen_pb2
from tfx.proto import evaluator_pb2
from tfx.proto import pusher_pb2
from tfx.proto import trainer_pb2
from tfx.proto import tuner_pb2
from tfx.types import Channel
from tfx.types.standard_artifacts import Model
from tfx.types.standard_artifacts import ModelBlessing
from tfx.types.standard_artifacts import Schema

from typing import Optional, Dict, List, Text, Union, Any

import features

TRANSFORM_MODULE_FILE='preprocess.py'
TRAIN_MODULE_FILE='train.py'

def create_pipeline(
    pipeline_name: Text, 
    pipeline_root: Text,
    serving_model_uri: Text, 
    data_root_uri: Union[Text, data_types.RuntimeParameter],
    schema_folder_uri: Union[Text, data_types.RuntimeParameter], 
    train_steps: Union[int, data_types.RuntimeParameter],
    eval_steps: Union[int, data_types.RuntimeParameter],
    beam_pipeline_args: List[Text],
    trainer_custom_executor_spec: Optional[executor_spec.ExecutorSpec] = None,
    trainer_custom_config: Optional[Dict[Text, Any]] = None, 
    enable_tuning: Optional[bool] = False,      
    enable_cache: Optional[bool] = False,
    metadata_connection_config: Optional[metadata_store_pb2.ConnectionConfig] = None) -> pipeline.Pipeline:

    """Trains and deploys the Keras Covertype Classifier with TFX and AI Platform Pipelines."""
  
    # Brings data into the pipeline and splits the data into training and eval splits
    output_config = example_gen_pb2.Output(
      split_config=example_gen_pb2.SplitConfig(splits=[
          example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=4),
          example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=1)
      ]))
  
    examplegen = CsvExampleGen(input_base=data_root_uri)
  
    # Computes statistics over data for visualization and example validation.
    statisticsgen = StatisticsGen(examples=examplegen.outputs.examples)
  
    # Generates schema based on statistics files. Even though, we use user-provided schema
    # we still want to generate the schema of the newest data for tracking and comparison
    schemagen = SchemaGen(statistics=statisticsgen.outputs.statistics)
  
    # Import a user-provided schema
    import_schema = ImporterNode(
        instance_name='import_user_schema',
        #source_uri=SCHEMA_FOLDER,
        source_uri=schema_folder_uri,
        artifact_type=Schema)
  
    # Performs anomaly detection based on statistics and data schema.
    examplevalidator = ExampleValidator(
        statistics=statisticsgen.outputs.statistics, 
        schema=import_schema.outputs.result)
  
    # Performs transformations and feature engineering in training and serving.
    transform = Transform(
        examples=examplegen.outputs.examples,
        schema=import_schema.outputs.result,
        module_file=TRANSFORM_MODULE_FILE)
  
    # Tunes the hyperparameters for model training based on user-provided Python
    # function. Note that once the hyperparameters are tuned, you can drop the
    # Tuner component from pipeline and feed Trainer with tuned hyperparameters.
    if enable_tuning:
        # The Tuner component launches 1 AI Platform Training job for flock management.
        # For example, 3 workers (defined by num_parallel_trials) in the flock
        # management AI Platform Training job, each runs Tuner.Executor.
        tuner = Tuner(
            module_file=TRAIN_MODULE_FILE,
            examples=transform.outputs.transformed_examples,
            transform_graph=transform.outputs.transform_graph,        
            train_args={'num_steps': train_steps},
            eval_args={'num_steps': eval_steps},
            tune_args=tuner_pb2.TuneArgs(
                # num_parallel_trials=3 means that 3 search loops are running in parallel.
                num_parallel_trials=3),
            custom_config=custom_config)  
  
    # Trains the model using a user provided trainer function.
    trainer = Trainer(
        custom_executor_spec=trainer_custom_executor_spec,
        module_file=TRAIN_MODULE_FILE,
        transformed_examples=transform.outputs.transformed_examples,
        schema=import_schema.outputs.result,
        transform_graph=transform.outputs.transform_graph,
        hyperparameters=(tuner.outputs.best_hyperparameters if enable_tuning else None),      
        train_args={'num_steps': train_steps},
        eval_args={'num_steps': eval_steps},
        custom_config=trainer_custom_config
        )
  
    # Get the latest blessed model for model validation.
    resolver = ResolverNode(
        instance_name='latest_blessed_model_resolver',
        resolver_class=latest_blessed_model_resolver.LatestBlessedModelResolver,
        model=Channel(type=Model),
        model_blessing=Channel(type=ModelBlessing))
  
    # Uses TFMA to compute a evaluation statistics over features of a model.
    accuracy_threshold = tfma.MetricThreshold(
                  value_threshold=tfma.GenericValueThreshold(
                      lower_bound={'value': 0.5},
                      upper_bound={'value': 0.99}),
                  )
  
    metrics_specs = tfma.MetricsSpec(
                     metrics = [
                         tfma.MetricConfig(class_name='SparseCategoricalAccuracy',
                             threshold=accuracy_threshold),
                         tfma.MetricConfig(class_name='ExampleCount')])
  
    eval_config = tfma.EvalConfig(
      model_specs=[
          tfma.ModelSpec(label_key='Cover_Type')
      ],
      metrics_specs=[metrics_specs],
      slicing_specs=[
          tfma.SlicingSpec(),
          tfma.SlicingSpec(feature_keys=['Wilderness_Area'])
      ]
    )
    
    evaluator = Evaluator(
        examples=examplegen.outputs.examples,
        model=trainer.outputs.model,
        baseline_model=resolver.outputs.model,
        eval_config=eval_config
    )
  
    pusher = Pusher(
        model=trainer.outputs['model'],
        model_blessing=evaluator.outputs['blessing'],
        push_destination=pusher_pb2.PushDestination(
            filesystem=pusher_pb2.PushDestination.Filesystem(
                base_directory=serving_model_uri)))
  
    components=[
        examplegen, 
        statisticsgen,
        schemagen,      
        import_schema,
        examplevalidator,
        transform,
        trainer, 
        resolver, 
        evaluator, 
        pusher 
    ]
  
    if enable_tuning:
      components.append(tuner)
  
    return pipeline.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        enable_cache=enable_cache,
        beam_pipeline_args=beam_pipeline_args,
        metadata_connection_config=metadata_connection_config
    )
  
  
  