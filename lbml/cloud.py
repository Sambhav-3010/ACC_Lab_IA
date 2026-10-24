import json
import os
import time


def client(service):
    import boto3
    return boto3.client(service, region_name=os.getenv("AWS_REGION", "ap-south-1"))


def cloud_status():
    return [("Amazon S3", bool(os.getenv("LBML_S3_BUCKET")), "Experiment artifacts"), ("Amazon DynamoDB", bool(os.getenv("LBML_DDB_TABLE")), "Run summaries"), ("Amazon CloudWatch", bool(os.getenv("LBML_LOG_GROUP")), "Experiment events")]


def publish_run(results: dict):
    messages = []
    bucket = os.getenv("LBML_S3_BUCKET", "").strip()
    if bucket:
        key = f"runs/{results['scenario']}/{results['policy']}-{results['seed']}.json"
        client("s3").put_object(Bucket=bucket, Key=key, Body=json.dumps(results, default=str).encode(), ContentType="application/json")
        messages.append(f"S3 artifact uploaded: {key}")
    table = os.getenv("LBML_DDB_TABLE", "").strip()
    if table:
        item = {"run_id": {"S": f"{results['scenario']}-{results['policy']}-{results['seed']}"}, "scenario": {"S": results["scenario"]}, "policy": {"S": results["policy"]}, "avg_latency_s": {"N": str(results["avg_latency_s"])}, "overload_events": {"N": str(results["overload_events"])}, "created_at": {"N": str(int(time.time()))}}
        client("dynamodb").put_item(TableName=table, Item=item)
        messages.append("DynamoDB run summary saved")
    group = os.getenv("LBML_LOG_GROUP", "").strip()
    if group:
        logs = client("logs")
        stream = os.getenv("LBML_LOG_STREAM", "experiments")
        try:
            logs.create_log_stream(logGroupName=group, logStreamName=stream)
        except logs.exceptions.ResourceAlreadyExistsException:
            pass
        logs.put_log_events(logGroupName=group, logStreamName=stream, logEvents=[{"timestamp": int(time.time() * 1000), "message": json.dumps(results, default=str)}])
        messages.append("CloudWatch experiment event logged")
    return messages
