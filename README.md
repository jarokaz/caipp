# Cloud AI Platform Pipelines code samples

## Installing Cloud AI Platform Pipelines (Experimental) prerequisites

The following instructions have been tested with Cloud AI Platform Notebooks using a base (CPU) Python image.

Execute the following commands from the AI Platform Notebooks terminal.

### Authenticate to GCP and establish a security context

```
gcloud auth login
```

### Upgrade Python 3 `pip`

```
pip install pip==20.2.4 --upgrade 
```

### Install TFX

```
pip install --user tfx==0.27.0 --upgrade

```

### Install the latest version of KFP

```
pip install --user kfp --upgrade
```


### Install AI Platform (Unfied) Pipelines SDK

```
cd /tmp
gsutil cp gs://cloud-aiplatform-pipelines/releases/20210209/aiplatform_pipelines_client-0.1.0.caip20210209-py3-none-any.whl .
pip install --user aiplatform_pipelines_client-0.1.0.caip20210209-py3-none-any.whl --upgrade
cd
```


### Install AI Platform (Unified) SDK

```
pip install -U google-cloud-aiplatform --user
```
