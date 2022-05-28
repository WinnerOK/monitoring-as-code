from requests.auth import HTTPBasicAuth

from monitoring_as_code.binds.grafana.handlers.folder import FolderHandler
from monitoring_as_code.binds.grafana.resources import Folder

DEBUG = False
USERNAME = "admin"
PASSWORD = "admin"

PORT = 10050 if DEBUG else 3000
BASE_URL = f"http://localhost:{PORT}/api"
HEADERS = {}
AUTH = HTTPBasicAuth(USERNAME, PASSWORD)
handler = FolderHandler(BASE_URL, HEADERS, AUTH)

folder = Folder(title="sandbox_folder", uid="test-project-maac-folder1")

# read_folder = handler.read(folder.uid)

folder_created = handler.create(folder)


a = 3
