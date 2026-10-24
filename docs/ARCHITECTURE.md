# CloudBalancer architecture

```mermaid
flowchart LR
  U[Student / Demo User] --> UI[Streamlit Control Room]
  UI --> W[Workload Generator]
  W --> T[(Identical workload trace)]
  T --> R1[Round Robin]
  T --> R2[Least Loaded]
  T --> R3[ML Predictive Router]
  R3 --> F[Feature Builder]
  F --> M[Random Forest CPU Predictor]
  R1 --> C[Four-server simulator]
  R2 --> C
  M --> R3
  C --> ME[Metrics: latency, throughput, imbalance, overload]
  ME --> D[Dashboard comparison]
  D --> S3[(Amazon S3\nrun artifacts)]
  D --> DDB[(Amazon DynamoDB\nrun summaries)]
  D --> CW[(Amazon CloudWatch\nexperiment logs)]
```

The simulator is the experimental environment. AWS stores and observes experiment outputs; it is not presented as a claim that real production traffic is being balanced by AWS infrastructure.
