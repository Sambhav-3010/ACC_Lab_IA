# ML-Based Intelligent Cloud Load Balancing

This Lab IA project simulates a four-server cloud cluster and compares three routing policies: Round Robin, Least Loaded, and ML Predictive (Random Forest prediction of near-future server CPU).

The simulator is deterministic and uses synthetic workloads so the same requests can be evaluated fairly by every policy. The Streamlit dashboard presents workload shape, predictions, server utilization, latency, overload events, and policy comparison.

## Run locally

```powershell
cd "C:\Users\sambh\Desktop\ACC Theory IA\Lab IA"
..\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m lbml.cli demo --scenario E3 --duration 180
streamlit run dashboard\app.py
```

The dashboard works offline. AWS is optional at runtime and is enabled by `.env.aws.generated` after `deploy_aws.ps1` is run.

## AWS component

The optional cloud layer uses Amazon S3 for experiment artifacts, DynamoDB for run summaries, and CloudWatch Logs for experiment events. It does not claim that the local simulator itself is deployed as a production load balancer.

## Project truth

CPU, latency, throughput, imbalance, and overload values are simulated measurements from the queueing model. Routing and inference overhead are measured by the local Python process. Results must be described as results from the simulated cluster.
