# DevOps Microservices Lab

A small microservices application designed for a Professional Master's DevOps course.

## Services

- Product Service: FastAPI, port 8001
- Order Service: FastAPI, port 8002
- PostgreSQL databases are planned for a later TP

For TP2, students only containerize and run the two stateless services.

## Run locally without Docker

### Product Service

```bash
cd product-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8001
```

### Order Service

```bash
cd order-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8002
```

## Intended evolution across the TPs

TP2: Docker basics and running containers

TP3: Dockerfiles and image construction

TP4: Docker Compose and service-to-service networking

TP5: Tests

TP6: GitHub Actions CI

TP7: Security checks

TP8: Registry and image scanning

TP9-10: Kubernetes

TP11: CI/CD + deployment automation

Terraform can be added after the students understand containers and Kubernetes. It should provision infrastructure, not replace Docker/Kubernetes concepts.

## Teacher build for TP2

Build the reference images from the project root:

```bash
docker build -f teacher-solution/product.Dockerfile -t product-service:tp2 .
docker build -f teacher-solution/order.Dockerfile -t order-service:tp2 .
```

Then follow `docs/TP2_Docker.md`.

## Terraform roadmap

Terraform is intentionally introduced after students understand Docker and Kubernetes:

- Terraform TP: variables, providers, resources, state
- Provision a local or cloud environment
- Later connect Terraform with Kubernetes resources
- Final architecture: Terraform provisions infrastructure; Kubernetes orchestrates containers; GitHub Actions automates delivery
