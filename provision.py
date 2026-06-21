# provision.py — create the resource group and storage account in code

import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku

SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RG = os.environ["AZURE_RG"]
LOCATION = os.environ["AZURE_LOCATION"]
ACCOUNT = os.environ["STORAGE_ACCOUNT_NAME"]

cred = DefaultAzureCredential()

resource_client = ResourceManagementClient(cred, SUBSCRIPTION_ID)
storage_client = StorageManagementClient(cred, SUBSCRIPTION_ID)

# Create or update resource group
resource_client.resource_groups.create_or_update(
    RG,
    {"location": LOCATION}
)

print(f"Resource group '{RG}' ready in {LOCATION}.")

# Create storage account
params = StorageAccountCreateParameters(
    sku=Sku(name="Standard_LRS"),
    kind="StorageV2",
    location=LOCATION,
    enable_https_traffic_only=True,
    minimum_tls_version="TLS1_2",
    allow_blob_public_access=False
)

print(f"Creating storage account '{ACCOUNT}'...")
poller = storage_client.storage_accounts.begin_create(RG, ACCOUNT, params)
account = poller.result()

print("Storage account created successfully.")
print("Account name:", account.name)

if account.primary_endpoints and account.primary_endpoints.web:
    print("Primary web endpoint:", account.primary_endpoints.web)
else:
    print("Primary web endpoint will be available after static website hosting is enabled.")
