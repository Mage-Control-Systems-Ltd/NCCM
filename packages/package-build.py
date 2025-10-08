import shutil
import json
import os
import zipfile
import hashlib

# Constants
ARCHIVE = "nccm-archive"
PCM = "pcm"
ACTION_FILE = "nccm_action.py"
GUI_FILE = "nccm_gui.py"
ICON24_FILE = "icon24.png"
ICON64_FILE = "icon64.png"
METADATA_JSON = "metadata.json"
PLUGIN_JSON = "plugin.json"
REQUIREMENTS = "requirements.txt"


def get_sha_256(filename: str):
    data = open(filename, "rb").read()

    return hashlib.sha256(data).hexdigest()


def get_package_stats(filename: str) -> tuple:
    instsize = 0
    z = zipfile.ZipFile(filename, "r")
    for entry in z.infolist():
        if not entry.is_dir():
            instsize += entry.file_size

    return get_sha_256(filename), os.path.getsize(filename), instsize


def get_version(path: str) -> str:
    version = "error"
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            line_split = line.split(" ")
            if line_split[0] == "__version__":
                version = line_split[2]
                break
    return version


if __name__ == "__main__":
    # Create paths
    dir = os.path.dirname(os.path.realpath(__file__))
    archive_path = os.path.join(dir, ARCHIVE)
    plugins_path = os.path.join(archive_path, "plugins")
    resources_path = os.path.join(archive_path, "resources")
    pcm_path = os.path.join(dir, PCM)
    action_file_path = os.path.join("..", ACTION_FILE)
    gui_file_path = os.path.join("..", GUI_FILE)
    requirements_file_path = os.path.join("..", REQUIREMENTS)
    plugin_json_path = os.path.join("..", PLUGIN_JSON)
    icon24_path = os.path.join("..", os.path.join("images", ICON24_FILE))
    icon64_path = os.path.join("..", os.path.join("images", ICON64_FILE))

    # Get the plugin version
    version = get_version(action_file_path).strip().removeprefix('"').removesuffix('"')
    archive_version_str = ARCHIVE + version + ".zip"

    # Remove directories if they exist
    if os.path.exists(archive_path):
        shutil.rmtree(archive_path)

    if os.path.exists(pcm_path):
        shutil.rmtree(pcm_path)

    if os.path.exists(archive_version_str):
        os.remove(archive_version_str)

    # Create archive path
    os.mkdir(archive_path)

    # Create plugins/ and contents
    os.mkdir(plugins_path)
    shutil.copy(action_file_path, plugins_path)
    shutil.copy(gui_file_path, plugins_path)
    shutil.copy(icon24_path, plugins_path)
    shutil.copy(plugin_json_path, plugins_path)
    shutil.copy(requirements_file_path, plugins_path)

    os.rename(
        os.path.join(plugins_path, ICON24_FILE), os.path.join(plugins_path, "icon.png")
    )

    # Create resources/ and contents
    os.mkdir(resources_path)
    shutil.copy(icon64_path, resources_path)
    os.rename(
        os.path.join(resources_path, ICON64_FILE),
        os.path.join(resources_path, "icon.png"),
    )

    # Copy metadata.json to plugins/
    shutil.copy(METADATA_JSON, archive_path)

    # Load metadata.json
    with open(os.path.join(archive_path, METADATA_JSON), "r") as f:
        metadata = json.load(f)

    # Update version string and save
    with open(os.path.join(archive_path, METADATA_JSON), "w") as f:
        metadata["versions"][0].update(
            {
                "version": version,
            }
        )
        json.dump(metadata, f, indent=4)

    # Create zip and rename with version string
    shutil.make_archive(ARCHIVE, "zip", ARCHIVE)
    os.rename(ARCHIVE + ".zip", archive_version_str)

    # Get packages stats to fill the download_sha256, download_size, and install size
    (download_sha256, download_size, install_size) = get_package_stats(
        ARCHIVE + version + ".zip"
    )

    # Create pcm/ path and contents
    os.makedirs(pcm_path)
    shutil.copy(icon64_path, pcm_path)
    os.rename(os.path.join(pcm_path, ICON64_FILE), os.path.join(pcm_path, "icon.png"))
    shutil.copy(os.path.join(archive_path, METADATA_JSON), pcm_path)

    # Load metadata.json
    with open(os.path.join(pcm_path, METADATA_JSON), "r") as f:
        metadata = json.load(f)
        version_dict = metadata["versions"][0]

    # Update versions field with most recent version, sha256, etc. and save
    with open(os.path.join(pcm_path, METADATA_JSON), "w") as f:
        metadata["versions"][0].update(
            {
                "version": version,
                "download_sha256": download_sha256,
                "download_size": download_size,
                "download_url": f"https://github.com/Mage-Control-Systems-Ltd/NCCM/releases/download/v{version}/{archive_version_str}",
                "install_size": install_size,
            }
        )
        json.dump(metadata, f, indent=4)
