# Icebox

## Installation

### Pypi dependencies

``` bash
pip install -r requirements.txt
```

## Configuration

As a prerequisite, you will need to configure your storage.
1. [Google Cloud Storage](#configure_storage_gcp)

Use the command `python icebox.py config` to configure your icebox.

```
$ python icebox.py config
Choose a cloud storage service provider:
	[1] Google Cloud Storage (GCP)
	[2] Amazon S3 (AWS)
```
Currently `[1] Google Cloud Storage (GCP)` is the only supported option.

### GCP

Provide credentials.
```
Enter path for the GCP service account credentials:
```
Enter the download path of the credentials downloaded while [configuring storage](#configure_storage_gcp).

Enter your preferred location.
```
Enter preferred GCP location (https://cloud.google.com/storage/docs/locations) [asia-south1]:
```

Enter the name of the bucket to be used.
```
Enter a unique bucket name or map to an existing one. Leave blank to use auto generated name (something-utterly-random-here):
```
If you wish to use an existing bucket or are setting up a new system to interact with an existing icebox, put the name of bucket following the `icebox_` in your [Cloud Storage Browser](https://console.cloud.google.com/storage/browser).


## Configure Storage

### Google Cloud Storage<a name="configure_storage_gcp"></a>

To use the `Google Cloud Storage` as the backup for icebox, we'll need to set up a project and enable the `Cloud Storage API` in `GCP`.

1. [Select a newly created or an existing project.](https://console.cloud.google.com/project)

2. [Enable billing for the project.](https://cloud.google.com/billing/docs/how-to/modify-project#enable_billing_for_a_project)

3. [Create a role in the project.](https://cloud.google.com/iam/docs/creating-custom-roles) Assign the following permissions to the role.
  * storage.buckets.create
  * storage.buckets.get
  * storage.buckets.list
  * storage.objects.create
  * storage.objects.delete
  * storage.objects.get
  * storage.objects.list
  * storage.objects.update


4. [Create a service account in the project.](https://cloud.google.com/iam/docs/creating-managing-service-accounts) Assign the role created in step 3 to this service account.

5. [Create a set of JSON keys for the service account.](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) Store the credentials locally.
