from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission"
ASSETS = OUT / "assets"
OUT.mkdir(exist_ok=True); ASSETS.mkdir(exist_ok=True)


def font(size, bold=False):
    path = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def diagram_assets():
    bg, white, muted, orange, lime, blue = "#101315", "#F4F0E8", "#A9AAA5", "#FF8A3D", "#B6F36B", "#7EB6FF"

    def canvas(title, subtitle):
        im = Image.new("RGB", (1800, 1000), bg); d = ImageDraw.Draw(im)
        d.text((65, 42), title, font=font(46, True), fill=white); d.text((68, 105), subtitle, font=font(23), fill=muted)
        for x in range(0, 1800, 60): d.line((x, 175, x, 1000), fill="#202528", width=1)
        for y in range(175, 1000, 60): d.line((0, y, 1800, y), fill="#202528", width=1)
        return im, d

    def card(d, box, title, body, color):
        x, y, w, h = box
        d.rounded_rectangle((x, y, x+w, y+h), radius=12, fill="#1B2022", outline=color, width=4)
        d.text((x+22, y+18), title, font=font(27, True), fill=white)
        d.multiline_text((x+22, y+66), body, font=font(21), fill=muted, spacing=8)

    def arrow(d, a, b, color=orange):
        d.line((a[0], a[1], b[0], b[1]), fill=color, width=5)
        d.polygon([(b[0], b[1]), (b[0]-16, b[1]-10), (b[0]-16, b[1]+10)], fill=color)

    im, d = canvas("CloudBalancer architecture", "ML routing controller + simulated cluster + AWS experiment layer")
    card(d, (70, 365, 275, 150), "Control room", "Streamlit\nscenario + metrics", blue)
    card(d, (435, 260, 285, 160), "Workload", "seeded trace\nstable / ramp / spike", orange)
    card(d, (435, 555, 285, 160), "ML predictor", "Random Forest\nfuture CPU estimate", lime)
    card(d, (870, 300, 300, 280), "Routing policies", "Round Robin\nLeast Loaded\nML Predictive", blue)
    card(d, (1320, 240, 330, 160), "Four servers", "S0  S1  S2  S3\ncapacity + active work", orange)
    card(d, (1320, 530, 330, 160), "Metrics", "latency • p95\nimbalance • overload", lime)
    card(d, (900, 780, 270, 130), "Amazon S3", "run artifacts", orange)
    card(d, (1210, 780, 270, 130), "DynamoDB", "run summary", blue)
    card(d, (1520, 780, 220, 130), "CloudWatch", "events", lime)
    arrow(d, (345, 420), (435, 340)); arrow(d, (345, 455), (435, 635)); arrow(d, (720, 340), (870, 390)); arrow(d, (720, 635), (870, 485)); arrow(d, (1170, 390), (1320, 320)); arrow(d, (1170, 490), (1320, 610)); arrow(d, (1080, 580), (1030, 780)); arrow(d, (1250, 580), (1340, 780)); arrow(d, (1450, 690), (1630, 780))
    im.save(ASSETS / "lab_architecture.png")

    im, d = canvas("Policy decision workflow", "The model output enters the routing decision")
    steps = [("01", "Generate", "same seeded\nrequest trace", orange), ("02", "Observe", "CPU, active work,\ncapacity, arrival rate", blue), ("03", "Predict", "future CPU\nwith Random Forest", lime), ("04", "Route", "avoid hot servers\nselect lowest score", orange), ("05", "Evaluate", "latency, p95,\nimbalance, overload", blue)]
    x = 65
    for i, (num, title, body, col) in enumerate(steps):
        card(d, (x, 390, 300, 190), f"{num}  {title}", body, col)
        if i < 4: arrow(d, (x+300, 485), (x+345, 485))
        x += 350
    im.save(ASSETS / "lab_workflow.png")

    im, d = canvas("Evaluation dimensions", "Every policy is measured on the same workload")
    items = [("Latency", "average + p95", orange), ("Throughput", "requests / second", lime), ("Imbalance", "distribution CV", blue), ("Overload", "threshold events", orange), ("Overhead", "routing microseconds", lime)]
    for i, (title, body, col) in enumerate(items):
        card(d, (90 + (i % 3) * 560, 300 + (i // 3) * 300, 430, 190), title, body, col)
    im.save(ASSETS / "lab_metrics.png")


def run(text, size=22, bold=False, italic=False, color="1F2937"):
    props = f'<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/><w:color w:val="{color}"/>'
    if bold: props += '<w:b/><w:bCs/>'
    if italic: props += '<w:i/><w:iCs/>'
    return f'<w:r><w:rPr>{props}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def paragraph(text, size=22, bold=False, italic=False, align=None, after=130):
    alignment = f'<w:jc w:val="{align}"/>' if align else ''
    return f'<w:p><w:pPr><w:spacing w:after="{after}"/>{alignment}</w:pPr>{run(text, size, bold, italic)}</w:p>'


def heading(text, level=1):
    return paragraph(text, 32 if level == 1 else 25, True, after=190)


def bullets(items):
    return ''.join(paragraph("• " + item, 21, after=75) for item in items)


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def image(rid, name, width=6200000, height=3300000):
    return f'''<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><wp:extent cx="{width}" cy="{height}"/><wp:docPr id="10" name="{name}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="1" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{width}" cy="{height}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''


def document_body():
    body = []
    body += [paragraph("ML-BASED LOAD BALANCING AND RESOURCE ALLOCATION", 38, True, align="center", after=180), paragraph("Intelligent Cloud Workload Management Using Workload Prediction", 28, True, align="center", after=300), paragraph("Cloud Computing Laboratory CA | Samiksha Sharma • Sambhav Mani Tripathi • Sahil Belchada", 20, italic=True, align="center", after=430)]
    body += [heading("Abstract"), paragraph("CloudBalancer is a machine-learning-assisted load-balancing prototype for intelligent cloud workload management. It creates identical synthetic workloads, routes requests through a four-server simulated cluster, and compares Round Robin, Least Loaded, and ML Predictive policies. A Random Forest estimates near-future CPU utilization, while the dashboard reports latency, throughput, server imbalance, overload events, and measured routing overhead. Amazon S3, DynamoDB, and CloudWatch Logs provide cloud-backed experiment storage, run summaries, and observability. The project is deliberately presented as a controlled simulation rather than a claim of production cloud performance.")]
    body += [page_break(), heading("1. Introduction and Real-World Context"), paragraph("Cloud applications experience traffic that changes over time. A server may be healthy at the moment a request arrives but become overloaded after a burst of expensive requests. Round Robin distributes requests in sequence, while Least Loaded reacts to current state. Both approaches can make decisions without considering what is likely to happen next. CloudBalancer investigates whether a workload prediction can improve request allocation."), paragraph("The project is designed for a laboratory demonstration. A deterministic simulator is preferable to an uncontrolled collection of real processes because every policy can receive the same request trace and the experiment can be repeated with a fixed seed. This makes the results explainable and reduces the infrastructure required for a student project."), heading("Objectives", 2), bullets(["Generate stable, ramp, spike, and heterogeneous-capacity workloads.", "Simulate a four-server cluster with explicit capacity and active work.", "Train or load a Random Forest CPU-utilization predictor.", "Compare Round Robin, Least Loaded, and ML Predictive routing.", "Measure latency, throughput, imbalance, overload events, and overhead.", "Use AWS services to store and observe selected experiment outputs."])]
    body += [page_break(), heading("2. Problem Statement, Scope, and Requirements"), heading("Problem Statement", 2), paragraph("Static or purely reactive load-balancing policies may distribute requests without anticipating future resource pressure. The proposed system predicts near-future server utilization and combines that prediction with current utilization when selecting a destination server. The system must evaluate this approach against transparent baselines rather than assuming that machine learning always improves every metric."), heading("Functional Requirements", 2), bullets(["Generate a reproducible workload from a scenario and seed.", "Model four servers with different capacities when required.", "Route every request using three comparable policies.", "Display observed and predicted utilization information.", "Calculate average latency, p95 latency, throughput, imbalance, and overload events.", "Allow the user to publish an ML run to S3, DynamoDB, and CloudWatch."]), heading("Scope Boundaries", 2), paragraph("The MVP does not provision real virtual machines, replace an enterprise load balancer, implement Kubernetes, or claim real network latency. Autoscaling, real HTTP workers, authentication, and production observability are future extensions. This boundary keeps the experiment achievable and academically honest.")]
    body += [page_break(), heading("3. System Architecture and Data Flow"), paragraph("The application is divided into a user interface, workload generator, routing policies, ML predictor, simulated cluster, evaluation layer, and optional AWS publication layer. The same workload is evaluated by each policy so the comparison is paired and reproducible."), image("rId2", "lab_architecture.png"), paragraph("Figure 1. CloudBalancer system architecture.", 18, italic=True, align="center"), heading("Data Flow", 2), bullets(["The demonstrator selects a scenario, duration, and seed in Streamlit.", "The workload generator creates requests with arrival times and CPU work.", "Each policy receives the same generated trace.", "The ML policy builds features and estimates future CPU utilization.", "A server is selected using the policy-specific routing rule.", "The simulator records outcomes and calculates comparison metrics.", "The selected ML result can be sent to AWS cloud services."])]
    body += [page_break(), heading("4. Machine-Learning Method and Routing Policies"), paragraph("The predictor uses current CPU, recent CPU behavior, active requests, arrival rate, and server capacity. A Random Forest Regressor is used because it can represent nonlinear relationships between workload pressure and utilization without requiring feature scaling. A fixed random seed makes the training path reproducible."), image("rId3", "lab_workflow.png"), paragraph("Figure 2. From identical workload to policy evaluation.", 18, italic=True, align="center"), heading("Routing Policies", 2), bullets(["Round Robin: selects servers in cyclic order and provides a simple baseline.", "Least Loaded: selects the server with the lowest current simulated CPU.", "ML Predictive: combines predicted CPU and live CPU, avoids servers above the overload threshold when possible, and falls back safely when all servers are hot."]), heading("Fallback Behavior", 2), paragraph("The controller must not stop because a prediction is unavailable. It can use current utilization as a persistence estimate and ultimately select the least-bad eligible server. This is important in a cloud system because graceful degradation is preferable to a routing-controller crash.")]
    body += [page_break(), heading("5. Experimental Design and Metrics"), paragraph("Four scenarios are available. E1 represents stable traffic. E2 gradually increases the arrival rate. E3 introduces a sudden spike and is the main demonstration scenario. E4 uses heterogeneous capacities of 0.5, 1.0, 1.0, and 1.5 so the experiment can show why equal request counts are not equal resource usage."), image("rId4", "lab_metrics.png"), paragraph("Figure 3. Evaluation dimensions used by the dashboard.", 18, italic=True, align="center"), heading("Metrics", 2), bullets(["Average latency: mean simulated completion delay.", "P95 latency: the value below which 95 percent of simulated requests fall.", "Throughput: completed requests divided by simulation duration.", "Imbalance: coefficient of variation of request distribution across servers.", "Overload events: requests routed while the selected server crosses the 0.8 threshold.", "Routing overhead: local execution time measured with time.perf_counter()."])]
    body += [page_break(), heading("6. Streamlit Dashboard and User Experience"), paragraph("The Lab IA interface is intentionally different from the Theory IA InvoiceFlow interface. It uses an operations-control visual language: graphite panels, orange action controls, lime health indicators, monospace labels, and a dense benchmark layout. It is designed to look like an experiment control plane rather than a document-processing workspace."), heading("What the Dashboard Shows", 2), bullets(["Control Plane: scenario, duration, seed, and experiment execution.", "AWS Telemetry: whether S3, DynamoDB, and CloudWatch are configured.", "Policy Benchmark Matrix: one row for each routing policy and its metrics.", "Pressure Profile: comparative latency and overload charts.", "Request Allocation: how requests are distributed among servers.", "Server Telemetry / Predictive Trace: observed utilization and ML prediction data.", "Publish ML Run to AWS: sends the selected result to the configured services."]), paragraph("The dashboard is used to demonstrate the research question: when traffic changes, does a predictive routing policy allocate requests more intelligently than a static or purely reactive baseline? It is not only a visual report; it is the experiment control surface.")]
    body += [page_break(), heading("7. AWS Cloud Services"), heading("Amazon S3", 2), paragraph("S3 stores experiment artifacts and provides durable object storage for the cloud-backed experiment workflow. The bucket is private and public access blocking is enabled by the deployment script."), heading("Amazon DynamoDB", 2), paragraph("DynamoDB stores a compact structured summary for each published run. The run identifier is the partition key, allowing the demonstration to show managed NoSQL persistence without operating a database server."), heading("Amazon CloudWatch Logs", 2), paragraph("CloudWatch Logs receives a structured event when a run is published. This demonstrates cloud observability and makes the experiment event visible outside the local dashboard."), heading("Credentials and Security", 2), bullets(["The project does not write AWS secret keys into source files.", "Boto3 uses the AWS CLI credential provider chain.", "Only synthetic experiment data should be used in the demonstration.", "A production deployment should use an IAM role or least-privilege user rather than the root account."]), heading("Cloud Computing Contribution", 2), paragraph("The cloud contribution is explicit: S3 provides object storage, DynamoDB provides managed structured persistence, and CloudWatch provides managed logging. The simulator remains local and is described honestly as the experimental environment.")]
    body += [page_break(), heading("8. Testing, Results, and Limitations"), heading("Automated Testing", 2), paragraph("The test suite verifies that seeded workloads are reproducible, generated work is positive, all three policies return metrics, and the ML policy executes a routing path. The validated local test result was four passing tests."), heading("Manual Acceptance Tests", 2), bullets(["Run E3 with seed 101 and confirm all three policy rows appear.", "Inspect average and p95 latency values.", "Inspect request distribution across S0, S1, S2, and S3.", "Inspect the utilization trace and overload threshold.", "Publish the ML run and verify the S3, DynamoDB, and CloudWatch confirmations.", "Repeat with E4 to demonstrate heterogeneous capacities."]), heading("Limitations", 2), bullets(["CPU and latency are simulated rather than measured from real servers.", "Synthetic traffic may not represent a production workload.", "The local dashboard is not an autoscaling distributed service.", "The MVP does not include authentication or accounting-system integration.", "ML may not outperform baselines in every scenario; that is a result to evaluate, not a guarantee."])]
    body += [page_break(), heading("9. Conclusion, Future Work, and References"), paragraph("CloudBalancer places an ML model inside a genuine routing decision loop and evaluates it against transparent baselines. The project demonstrates workload generation, resource-aware routing, model inference, metrics, a distinct analytical dashboard, and AWS-backed experiment storage and monitoring. Its strongest academic feature is that it makes a testable claim rather than presenting machine learning as automatically superior."), heading("Future Enhancements", 2), bullets(["Connect the controller to real FastAPI worker processes.", "Add an advisory autoscaling recommendation.", "Add server-failure and monitoring-failure scenarios.", "Store detailed time-series runs in S3 and query summaries from DynamoDB.", "Deploy the dashboard using a managed cloud hosting platform."]), heading("References", 2), bullets(["Amazon S3: https://docs.aws.amazon.com/s3/", "Amazon DynamoDB: https://docs.aws.amazon.com/amazondynamodb/", "Amazon CloudWatch Logs: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIs.html", "Boto3: https://docs.aws.amazon.com/boto3/latest/", "scikit-learn Random Forest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html", "Streamlit: https://docs.streamlit.io/", "NumPy and pandas documentation: https://numpy.org/doc/stable/ and https://pandas.pydata.org/docs/"]), heading("Demonstration Notes", 2), bullets(["Start the dashboard with the Lab IA virtual environment.", "Select E3, duration 180, and seed 101.", "Run the comparison and explain the matrix before discussing the charts.", "Publish the ML run only after showing the local metrics.", "State clearly that cluster performance values are simulated."]) ]
    return ''.join(body)


def make_docx():
    content = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
    rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    docrels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/lab_architecture.png"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/lab_workflow.png"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/lab_metrics.png"/></Relationships>'
    styles = '<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="22"/></w:rPr></w:style></w:styles>'
    document = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><w:body>{document_body()}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1100" w:right="1100" w:bottom="1100" w:left="1100"/></w:sectPr></w:body></w:document>'
    with ZipFile(OUT / "ML_Load_Balancing_Report.docx", "w", ZIP_DEFLATED) as archive:
        for name, data in {"[Content_Types].xml": content, "_rels/.rels": rels, "word/document.xml": document, "word/styles.xml": styles, "word/_rels/document.xml.rels": docrels}.items():
            archive.writestr(name, data)
        for name in ["lab_architecture.png", "lab_workflow.png", "lab_metrics.png"]:
            archive.write(ASSETS / name, "word/media/" + name)


if __name__ == "__main__":
    diagram_assets(); make_docx(); print("Created submission/ML_Load_Balancing_Report.docx")
