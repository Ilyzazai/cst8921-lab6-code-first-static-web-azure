# deploy.py
# Purpose:
# Upload all files from the local "site/" folder to the Azure Storage
# static website container named "$web".
#
# This script also sets:
# 1. Correct content types, so the browser renders files correctly.
# 2. Cache-Control headers, so HTML updates quickly but static assets can cache longer.

import os
import mimetypes
import pathlib

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings


# Read the Azure Storage account name from the environment variable.
# Example: cst8921lab6ilyas01
ACCOUNT = os.environ["STORAGE_ACCOUNT_NAME"]

# This is the local folder that contains our website files:
# site/index.html
# site/config.js
# site/404.html
SITE_DIR = pathlib.Path("site")

# Azure Storage static website hosting uses a special container called "$web".
# We upload our website files into this container.
CONTAINER = "$web"

# This is the Blob service data-plane endpoint.
# We use this endpoint to upload files into Azure Storage.
account_url = f"https://{ACCOUNT}.blob.core.windows.net"

# DefaultAzureCredential uses your current Azure login.
# Because you already ran "az login", Python can authenticate to Azure.
cred = DefaultAzureCredential()

# Create a client for the "$web" container.
# This client lets us upload files into the static website container.
container = BlobServiceClient(
    account_url=account_url,
    credential=cred
).get_container_client(CONTAINER)


def cache_control_for(path: pathlib.Path) -> str:
    """
    Return the Cache-Control value for each file.

    HTML files:
    - Use "no-cache" because HTML changes often.
    - The browser should check Azure for the latest version.

    Other files:
    - JavaScript, CSS, images, etc. can be cached longer.
    - In real projects, we usually use file versioning or hashing for these assets.
    """
    if path.suffix == ".html":
        return "no-cache"

    return "public, max-age=31536000, immutable"


# Check that the site folder exists before uploading.
if not SITE_DIR.exists():
    raise FileNotFoundError(
        "The 'site/' folder does not exist. Create site/index.html, site/config.js, and site/404.html first."
    )


# Go through every file inside the site/ folder.
for path in SITE_DIR.rglob("*"):

    # Skip folders. We only upload files.
    if not path.is_file():
        continue

    # Convert local path to Azure blob name.
    # Example:
    # site/index.html  -> index.html
    # site/config.js   -> config.js
    blob_name = path.relative_to(SITE_DIR).as_posix()

    # Guess the correct content type based on file extension.
    # Example:
    # .html -> text/html
    # .js   -> text/javascript or application/javascript
    #
    # If Python cannot guess it, use application/octet-stream as fallback.
    content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"

    # Choose the cache-control value for this file.
    cache_control = cache_control_for(path)

    # Open the local file in binary mode and upload it to Azure Storage.
    with path.open("rb") as file_data:
        container.upload_blob(
            name=blob_name,
            data=file_data,
            overwrite=True,
            content_settings=ContentSettings(
                content_type=content_type,
                cache_control=cache_control
            )
        )

    # Print useful deployment output for screenshot/report evidence.
    print(
        f"uploaded {blob_name:<15} "
        f"type={content_type:<25} "
        f"cache={cache_control}"
    )


print()
print("Deployment completed successfully.")
print("Open the static website endpoint:")
print(f"https://{ACCOUNT}.z13.web.core.windows.net/")
