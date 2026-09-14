import os

import boto3


def resolve_aws_region(profile):
    """Resolve the target AWS Region without imposing a us-east-1 default."""
    configured_region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    if configured_region:
        return configured_region

    profile_region = boto3.Session(profile_name=profile).region_name
    if profile_region:
        return profile_region

    raise RuntimeError(
        "No AWS Region is configured. Set AWS_DEFAULT_REGION (or AWS_REGION), "
        "or configure a region in the selected AWS profile."
    )
