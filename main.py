from urllib.parse import quote
import os
from datetime import datetime
import re

from typing import Union
from typing import Annotated, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import pandas as pd
import s3fs

BUCKET = "projet-budget-famille"

fs = s3fs.S3FileSystem(client_kwargs={"endpoint_url": "https://minio.lab.sspcloud.fr"})


class ProductData(BaseModel):
    """
    Pydantic BaseModel for representing the product data from the input JSON.

    Attributes:
        product (List[str]): The name of the product.
        code (List[str]): The code associated with the product.
        coicop (List[str]): The COICOP classification of the product.
        timestamp (List[str]): The timestamp when the data was recorded.
    """

    product: List[str]
    code: List[str]
    coicop: List[str]
    timestamp: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "product": ["Tablette graphique"],
                "code": ["05.4.0.3"],
                "coicop": ["Ustensiles et articles de cuisine (SD)"],
                "timestamp": ["2024-09-11T14:53:16.723Z"],
            }
        }


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def path_to_url_preview(path):
    # Base URL
    base_url = "https://datalab.sspcloud.fr/data-explorer?source="
    # Encode the path
    encoded_path = quote(f"s3://{path}")
    # Combine the base URL with the encoded path
    final_url = f"{base_url}{encoded_path}"
    return final_url


@app.post("/writes3/")
async def create_item(product: ProductData):

    now = datetime.now()
    day = now.strftime("%Y-%m-%d")
    path = f"{BUCKET}/data/output-annotation/{day=}".replace("'", "")

    try:
        existing_files = fs.ls(path)
        index_max_annot = int(
            pd.Series(
                [
                    int(re.search(r"annot(\d+)", files).group(1))
                    for files in existing_files
                ],
            ).max()
        )
        index_max_annot += 1
        filename = f"annot{index_max_annot}.parquet"
    except FileNotFoundError:
        print(f"The directory {path} does not exist or cannot be found.")
        filename = "annot1.parquet"

    path_s3 = f"{path}/{filename}"

    df = pd.DataFrame(product.dict())

    with fs.open(path_s3, "wb") as f:
        df.to_parquet(f)

    return {"filename": path_s3, "preview": path_to_url_preview(path_s3)}
