#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import wandb
import pandas as pd
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()


    logger.info("Downloading artifact")
    artifact_path = run.use_artifact(args.input_artifact).file()
    # read data
    df = pd.read_csv(artifact_path)
    # Impute nulls
    logger.info("Imputing nulls")
    df['reviews_per_month'].fillna(value=0, inplace=True)

    # Drop outliers
    logger.info("Dropping outliers")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()
    
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    filename = "processed_data.csv"
    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)
    artifact.wait()

    os.remove(filename)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This steps cleans the data")


    parser.add_argument(
        "--input_artifact",
        type=str,
        help='Fully qualified name for the artifact',
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help='Name for the W&B artifact that will be created',
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help='Type of the artifact to create',
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help='Description for the artifact',
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=int,
        help='Minimum price of the rental',
        required=False,
        default=10
    )

    parser.add_argument(
        "--max_price",
        type=int,
        help='Maximum price of the rental',
        required=False,
        default=350
    )

    args = parser.parse_args()

    go(args)
