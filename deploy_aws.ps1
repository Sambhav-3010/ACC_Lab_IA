$ErrorActionPreference = "Stop"
$identity = aws sts get-caller-identity --output json | ConvertFrom-Json
$region = aws configure get region
if ([string]::IsNullOrWhiteSpace($region)) { $region = "ap-south-1" }
$account = $identity.Account
$bucket = "lbml-experiments-$account-$region"
$table = "LBMLExperimentRuns"
$group = "/lbml/experiments"
$stream = "experiment-events"
Write-Host "Account: $account | Region: $region" -ForegroundColor Cyan
$ErrorActionPreference = "Continue"
aws s3api head-bucket --bucket $bucket 2>$null
if ($LASTEXITCODE -ne 0) {
  if ($region -eq "us-east-1") { aws s3api create-bucket --bucket $bucket --region $region | Out-Null }
  else { aws s3api create-bucket --bucket $bucket --region $region --create-bucket-configuration LocationConstraint=$region | Out-Null }
}
aws s3api put-public-access-block --bucket $bucket --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true | Out-Null
aws dynamodb describe-table --table-name $table --region $region 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { aws dynamodb create-table --table-name $table --attribute-definitions AttributeName=run_id,AttributeType=S --key-schema AttributeName=run_id,KeyType=HASH --billing-mode PAY_PER_REQUEST --region $region | Out-Null; aws dynamodb wait table-exists --table-name $table --region $region }
aws logs create-log-group --log-group-name $group --region $region 2>$null | Out-Null
aws logs create-log-stream --log-group-name $group --log-stream-name $stream --region $region 2>$null | Out-Null
$ErrorActionPreference = "Stop"
"AWS_REGION=$region`nLBML_S3_BUCKET=$bucket`nLBML_DDB_TABLE=$table`nLBML_LOG_GROUP=$group`nLBML_LOG_STREAM=$stream" | Set-Content -Path ".env.aws.generated" -Encoding ASCII
Write-Host "AWS resources ready. Configuration written to .env.aws.generated" -ForegroundColor Green
