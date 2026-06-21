# enable_static_website.py
# Purpose:
# This script enables Azure Storage static website hosting.
# It uses the Blob data-plane SDK, not the management SDK.
# Static website hosting creates/uses the special "$web" container.

import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, StaticWebsite

# Read the storage account name from the environment variable.
# Example: cst8921lab6ilyas01
ACCOUNT = os.environ["STORAGE_ACCOUNT_NAME"]

# Blob service URL for the storage account.
# This is the data-plane endpoint used by the Blob SDK.
account_url = f"https://{ACCOUNT}.blob.core.windows.net"

# DefaultAzureCredential uses your Azure CLI login from "az login".
cred = DefaultAzureCredential()

# Create a BlobServiceClient to work with blob service settings.
service = BlobServiceClient(account_url, credential=cred)

# Enable static website hosting.
# index_document tells Azure which file to load by default.
# error_document404_path tells Azure which page to show for missing pages.
#
# Important gotcha:
# The correct parameter is "error_document404_path".
# Do NOT write "error_document_404_path" because the SDK may silently ignore it.
service.set_service_properties(
    static_website=StaticWebsite(
        enabled=True,
        index_document="index.html",
        error_document404_path="404.html"
    )
)

print("Static website hosting enabled successfully.")

# Read back the service properties to verify the setting was actually applied.
# This helps detect silent mistakes like a wrong parameter name.
props = service.get_service_properties()
static_site = props.get("static_website")

print("Static website properties from Azure:")
print(static_site)
