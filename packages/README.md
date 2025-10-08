# NCCM Packages
To upload the plugin to the Plugin and Content Manager (PCM) two things are needed. First, the plugin has to be organised in an archive as shown [here](https://dev-docs.kicad.org/en/addons/index.html#_python_plugins) and then zipped to be downloaded and installed automatically by the PCM. This requirement is fulfilled under the `archive` directory and **ITS CONTENTS (NOT THE FOLDER)** is what should be zipped and placed as a release.

Second thing required is to upload the plugin to the PCM in KiCad, it requires a `metadata.json` file and an optional icon. See their repo [here](https://gitlab.com/kicad/addons/metadata) for more information. This requirement is fulfilled under the `pcm` directory, and is what is used as a PR to upload the metadata to the PCM. 

The metadata files in the two folders have some differences. The metadata file under `pcm` should contain the exact same information as the metadata file under `archive`, except that it must have only one version object corresponding to the package version, and it shouldn't have any `download_*` fields or the `install_size` field.

## Auto-packaging
Execute `package-build.py` to auto-package the plugin to fulfill the above requirements.

```
python package-build.py
```
