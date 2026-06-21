# cleanup.py
# Purpose:
# Delete the whole Azure resource group created for this lab.
#
# This removes:
# - Storage account
# - Static website files
# - Azure Function App
# - Azure Front Door
# - App Service plan
# - Any related resources inside the lab resource group
#
# The script is idempotent:
# If the resource group does not exist, it does not fail.

import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient


# Read subscription ID and resource group name from environment variables.
SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RG = os.environ["AZURE_RG"]

# Use current Azure CLI login identity.
cred = DefaultAzureCredential()

# Management-plane client for Azure Resource Groups.
client = ResourceManagementClient(cred, SUBSCRIPTION_ID)


# Check if the resource group exists before trying to delete it.
if client.resource_groups.check_existence(RG):
    print(f"Deleting resource group '{RG}'...")

    # begin_delete is a long-running operation.
    # .result() waits until Azure finishes deleting the resource group.
    client.resource_groups.begin_delete(RG).result()

    print("Resource group deleted successfully.")
else:
    print(f"Resource group '{RG}' does not exist. Nothing to delete.")
