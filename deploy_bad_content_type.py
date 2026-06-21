# deploy_bad_content_type.py
# Purpose:
# This script is only for the lab experiment.
# It uploads index.html WITHOUT setting content_type.
#
# Expected learning:
# Without content_type="text/html", the browser may download index.html
# instead of rendering it as a normal webpage.

import os
import pathlib

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Read the storage account name from environment variable.
ACCOUNT = os.environ["STORAGE_ACCOUNT_NAME"]

# The static website container in Azure Storage.
CONTAINER = "$web"

# Local HTML file for experiment.
INDEX_FILE = pathlib.Path("site/index.html")

# Blob service endpoint.
account_url = f"https://{ACCOUNT}.blob.core.windows.net"

# Use Azure CLI login identity.
cred = DefaultAzureCredential()

# Connect to $web container.
container = BlobServiceClient(
    account_url,
    credential=cred
).get_container_client(CONTAINER)

# Upload index.html without ContentSettings.
# This is intentionally wrong for the experiment.
with INDEX_FILE.open("rb") as file_data:
    container.upload_blob(
        name="index.html",
        data=file_data,
        overwrite=True
    )

print("Bad upload completed.")
print("index.html was uploaded without explicit content_type.")
print(f"Open: https://{ACCOUNT}.z13.web.core.windows.net/")
