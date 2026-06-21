# function_app.py
# Purpose:
# This Azure Function creates a simple HTTP API endpoint:
# GET /api/visits
#
# The function stores a visit counter in Azure Table Storage.
# Each time the browser calls the endpoint, the counter increases by 1.

import os
import json

import azure.functions as func
from azure.data.tables import TableServiceClient


# Create the Azure Functions app.
# ANONYMOUS means the browser can call this API without a function key.
# This is okay for this lab, but in production we would protect sensitive APIs.
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# Azure Functions uses AzureWebJobsStorage for its storage connection.
# For local testing, this can point to local Azurite or an Azure Storage account.
CONN = os.environ["AzureWebJobsStorage"]

# Table name where we store the counter.
TABLE = "visits"

# PartitionKey and RowKey identify one row/entity in Azure Table Storage.
# We use one entity to store one counter value.
PK = "site"
RK = "counter"


def get_table_client():
    """
    Create or get the Azure Table used for the visit counter.

    Table Storage is a simple NoSQL key-value style storage service.
    It stores entities using PartitionKey and RowKey.
    """
    service = TableServiceClient.from_connection_string(CONN)

    # This is safe to run multiple times.
    # If the table already exists, it will not fail.
    service.create_table_if_not_exists(TABLE)

    return service.get_table_client(TABLE)


@app.route(route="visits", methods=["GET"])
def visits(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP GET endpoint: /api/visits

    Flow:
    1. Connect to Table Storage.
    2. Read the existing counter.
    3. Add 1.
    4. Save the updated counter.
    5. Return JSON to the browser.
    """
    table = get_table_client()

    try:
        # Try to read the existing counter entity.
        entity = table.get_entity(partition_key=PK, row_key=RK)

        # Increase the counter.
        entity["count"] = entity["count"] + 1

        # Save the updated counter.
        table.update_entity(entity)

    except Exception:
        # If the counter does not exist yet, create it with count = 1.
        entity = {
            "PartitionKey": PK,
            "RowKey": RK,
            "count": 1
        }

        table.create_entity(entity)

    # Convert Python dictionary to JSON string.
    body = json.dumps({
        "count": entity["count"]
    })

    # Return JSON response.
    # Access-Control-Allow-Origin enables the browser to call this API
    # from the static website domain.
    return func.HttpResponse(
        body=body,
        status_code=200,
        mimetype="application/json",
        headers={
            "Access-Control-Allow-Origin": "*"
        }
    )
