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
Note that icebox buckets need to start with the `icebox_` prefix. In case you wish to create a bucket separately and use it for icebox, please ensure that it begins with the prefix. You can use either the full name of the bucket or the name following the `icebox_` prefix. Your existing storage buckets can be found in your [Cloud Storage Browser](https://console.cloud.google.com/storage/browser).

## Workflows

### Init<a name="workflow_init"></a>

Icebox can be used in any "initialized" folder. To initialize a folder, you need to use the following command.

```bash
python icebox.py init <path>
```

Icebox adds a unique ID to the initialized directory and creates an entry in the configured remote. You can check the details in the file created at `<path>/.icebox`.

Along with [clone](TODO), `init` is the first step in any workflow for using icebox.

### Freeze<a name="workflow_freeze"></a>

You can freeze files or folders inside an [initialized icebox](#workflow_init). A frozen file uploads the contents of the file to the remote storage and replaces it locally with a *preview* thumbnail (simply a 0 size file at the moment). Freezing a folder has the same effect as freezing all the files within it.

To freeze, use the following command.
```bash
python icebox.py freeze <path>
```

> A locally overwritten frozen file can be refrozen. This will replace the remote contents with the overwritten data.

### Thaw

A [frozen file](#workflow_freeze) or folder can be thawed. This command restores the original content of the file from the remote storage. Thawing a folder has the same effect as thawing all frozen files inside it.

To thaw, use the following command.
```bash
python icebox.py thaw <path>
```

> A locally overwritten frozen file cannot be thawed. The remote contents remain intact till the file is refrozen.

### List

You can list an icebox (remote or local). This allows you to check the contents of an icebox and navigate through it without necessarily cloning it.

To list remote iceboxes use the flag `-a` or `--remote`.
```bash
python icebox.py ls <path>
```

Without a path, this lists all the iceboxes in the configured storage. You can choose one to dig further. The path expects a folder-like pattern which should represent one complete directory structure in the icebox hierarchy.
```bash
python icebox.py ls <path>
```

Without the flag, the list command looks for the path locally (absolute or relative). Local listing provides additional information to the current status of the icebox.

* `*` represents a frozen file
* `~` represents a file that was modified locally after the freeze.
* no marker means that the file is either thawed or does not exist in the icebox.


## Configure Storage

### Google Cloud Storage<a name="configure_storage_gcp"></a>

To use the `Google Cloud Storage` as the backup for icebox, we'll need to set up a project and enable the `Cloud Storage API` in `GCP`.

1. [Select a newly created or an existing project.](https://console.cloud.google.com/project)

2. [Enable billing for the project.](https://cloud.google.com/billing/docs/how-to/modify-project#enable_billing_for_a_project)

3. [Create a role in the project.](https://cloud.google.com/iam/docs/creating-custom-roles) Assign the following permissions to the role.
  * serviceusage.services.use
  * storage.buckets.create
  * storage.buckets.get
  * storage.buckets.list
  * storage.objects.create
  * storage.objects.delete
  * storage.objects.get
  * storage.objects.list
  * storage.objects.update


4. [Create a service account in the project.](https://cloud.google.com/iam/docs/creating-managing-service-accounts) Assign the role created in step 3 to this service account.

5. [Create a set of JSON keys for the service account.](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) Store the credentials locally. The default location for creds is `~/.iceboxcfg/gcp/creds.json` but you can store it elsewhere and override the location during `icebox config`.
