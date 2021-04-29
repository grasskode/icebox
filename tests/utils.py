import shutil

from pathlib import Path

TEST_FOLDER = "test_data"


class TestUtils(object):
    """Utility class for tests."""

    def CreateTestFolder(self, path: str, prefix: Path = None) -> Path:
        dir_path = Path(TEST_FOLDER) if not prefix else prefix
        dir_path /= Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    def CreateTestFile(self, path: str, prefix: Path = None) -> Path:
        file_path = Path(TEST_FOLDER) if not prefix else prefix
        file_path /= Path(path)
        with open(file_path, 'w') as f:
            f.write("dummy data for non zero filesize.")
        return file_path

    def DeleteFolderAndContents(self, path: Path):
        shutil.rmtree(path)
