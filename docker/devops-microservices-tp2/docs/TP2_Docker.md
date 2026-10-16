# TP2 - Docker Fundamentals with Microservices

## Duration

90 minutes

## Context

You are joining a DevOps team that maintains two small services:

- `product-service`: exposes product information on port 8001
- `order-service`: creates orders and calls `product-service`

For this TP, the application code is already provided. Your objective is to understand Docker by running the services in containers.

## Learning objectives

By the end of the TP, you should be able to:

1. Explain the difference between an image and a container.
2. Pull an image from a registry.
3. Create and start a container.
4. Publish a container port to the host.
5. Inspect running containers.
6. Read container logs.
7. Execute a command inside a container.
8. Stop and remove containers.
9. Explain why microservices need network connectivity.

## Part 1 - Verify the tools (10 min)

```bash
docker --version
docker info
```

Record the Docker version in your report.

## Part 2 - Run an existing image (15 min)

```bash
docker pull nginx:alpine
docker run -d --name tp2-nginx -p 8080:80 nginx:alpine
docker ps
```

Open `http://localhost:8080` in a browser.

Then run:

```bash
docker logs tp2-nginx
docker inspect tp2-nginx
docker exec -it tp2-nginx sh
```

Inside the container, run:

```sh
ls
whoami
exit
```

Stop and remove the container:

```bash
docker stop tp2-nginx
docker rm tp2-nginx
```

## Part 3 - First microservice container (20 min)

In this TP, the teacher provides ready-made images for the two services, or the instructor may provide a pre-built image archive. Run the Product Service with:

```bash
docker run -d --name product-service -p 8001:8001 product-service:tp2
```

Verify:

```bash
docker ps
docker logs product-service
```

Test it:

```bash
curl http://localhost:8001/health
curl http://localhost:8001/products
```

Expected result includes:

```json
{"status":"ok","service":"product-service"}
```

## Part 4 - Run the Order Service (20 min)

Start the order service:

```bash
docker run -d --name order-service -p 8002:8002 \\
  -e PRODUCT_SERVICE_URL=http://host.docker.internal:8001 \\
  order-service:tp2
```

Test:

```bash
curl http://localhost:8002/health
```

Create an order:

```bash
curl -X POST http://localhost:8002/orders \\
  -H "Content-Type: application/json" \\
  -d '{"product_id":1,"quantity":2}'
```

Observe that Order Service calls Product Service before creating the order.

## Part 5 - Challenge (15 min)

Answer these questions:

1. What is the difference between `EXPOSE` and `-p` in Docker?
2. Why does the Order Service need the `PRODUCT_SERVICE_URL` environment variable?
3. What would happen if Product Service is stopped?
4. What is the difference between a Docker image and a container?
5. Why is `localhost` inside a container not automatically the host machine?

## Deliverable

Push a folder named `tp2` to your GitHub repository containing:

- the commands you executed,
- screenshots of `docker ps`,
- screenshots of both health endpoints,
- the answer to the five questions,
- one paragraph explaining how the two microservices communicate.

## Teacher note

TP2 intentionally avoids Dockerfiles and Compose. Those belong to TP3 and TP4. This keeps the cognitive load manageable and lets students first understand the image/container/runtime model.
