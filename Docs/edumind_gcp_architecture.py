# edumind_gcp_architecture.py
from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.client import User
from diagrams.onprem.database import PostgreSQL, InfluxDB
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.logging import Loki
from diagrams.onprem.tracing import Tempo
from diagrams.onprem.vcs import Github
from diagrams.onprem.container import Docker
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import React, FastAPI
from diagrams.programming.language import Python
from diagrams.gcp.compute import GKE
from diagrams.gcp.storage import GCS

# Graph Attributes
graph_attr = {
    "fontsize": "28",
    "bgcolor": "white",
    "pad": "0.8",
    "splines": "spline",
    "nodesep": "0.8",
    "ranksep": "1.2",
}

node_attr = {
    "fontsize": "11",
}

edge_attr = {
    "fontsize": "10",
}

with Diagram(
    "EduMind - GCP Cloud Native Architecture",
    show=False,
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    direction="TB",
    filename="edumind_gcp_architecture",
    outformat="png"
):
    
    # Users
    users = User("Students &\nEducators")
    
    # Frontend
    with Cluster("Frontend Layer"):
        frontend = React("React Dashboard\n(Recharts, Nivo)")
    
    # GCP Infrastructure
    with Cluster("Google Cloud Platform (GCP)"):
        
        # GKE Cluster
        with Cluster("Google Kubernetes Engine (GKE)"):
            
            # Ingress
            ingress = Nginx("Nginx\nIngress Controller")
            
            # API Layer
            with Cluster("Backend API Layer (Docker Containers)"):
                user_api = FastAPI("User Service\n(FastAPI)")
                course_api = FastAPI("Course Service\n(FastAPI)")
                assess_api = FastAPI("Assessment Service\n(FastAPI)")
            
            # ML Serving Layer
            with Cluster("AI/ML Prediction Services (Docker Containers)"):
                engagement = Python("Engagement\nTracker")
                learning = Python("Learning Style\nPredictor")
                xai = Python("XAI Engine\n(SHAP + LIME)")
            
            # ML Pipeline
            with Cluster("ML Pipeline Orchestration"):
                airflow = Airflow("Apache Airflow\n(ML Pipelines)")
            
            # Observability Stack
            with Cluster("LGTM Observability Stack"):
                loki = Loki("Loki\n(Logs)")
                grafana = Grafana("Grafana\n(Dashboards)")
                tempo = Tempo("Tempo\n(Traces)")
                mimir = Prometheus("Mimir\n(Metrics)")
        
        # Data Layer
        with Cluster("Data Persistence Layer"):
            postgres = PostgreSQL("PostgreSQL\n(Student Records)")
            timescale = InfluxDB("TimescaleDB\n(Engagement Logs)")
        
        # Storage
        with Cluster("Storage Layer"):
            gcs = GCS("GCS Buckets\n(Datasets + Models)")
            docker_registry = Docker("Container\nRegistry")
    
    # CI/CD Pipeline
    with Cluster("CI/CD & MLOps"):
        github = Github("GitHub Actions\n+ DVC")
    
    # Core ML
    with Cluster("ML Libraries"):
        sklearn = Python("Scikit-learn\n(Core ML)")
    
    # User Flow
    users >> frontend >> ingress
    
    ingress >> Edge(color="darkgreen") >> [user_api, course_api, assess_api]
    ingress >> Edge(color="purple") >> [engagement, learning, xai]
    
    # API to DB
    [user_api, course_api, assess_api] >> postgres
    [engagement, learning, xai] >> timescale
    
    # Observability connections
    [user_api, course_api, assess_api, engagement, learning, xai] >> Edge(style="dashed", color="gray") >> loki
    loki >> grafana
    tempo >> grafana
    mimir >> grafana
    
    # MLOps Flow
    github >> Edge(label="Trigger") >> airflow
    sklearn >> Edge(label="Train") >> airflow
    airflow >> gcs
    airflow >> Edge(style="dashed", color="blue", label="Deploy Models") >> [engagement, learning, xai]
    
    # Container builds
    github >> docker_registry
    docker_registry >> Edge(style="dashed", label="Pull Images") >> [user_api, course_api, assess_api, engagement, learning, xai]

print("GCP Architecture diagram generated as 'edumind_gcp_architecture.png'")
