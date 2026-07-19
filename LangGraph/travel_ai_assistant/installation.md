# Deploying Travel AI Assistant on a Local Kind Cluster

This guide walks you through setting up Kind (Kubernetes in Docker) on your machine and deploying the Travel AI Assistant from scratch.

---

## Prerequisites

You need the following installed:
- **Docker Desktop** (running) — Kind runs Kubernetes nodes as Docker containers
- **Ollama** (running on your host) — the LLM runs locally, not inside Kubernetes

---

## Step 1 — Install Kind

Kind runs a full Kubernetes cluster inside Docker containers. Install it with:

**Mac (Homebrew):**
```bash
brew install kind
```

**Mac (direct binary):**
```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.23.0/kind-darwin-arm64
chmod +x ./kind
mv ./kind /usr/local/bin/kind
```

> Use `kind-darwin-amd64` if you're on Intel Mac.

**Verify:**
```bash
kind version
```

---

## Step 2 — Install kubectl

kubectl is the CLI to talk to your Kubernetes cluster.

**Mac (Homebrew):**
```bash
brew install kubectl
```

**Verify:**
```bash
kubectl version --client
```

---

## Step 3 — Create the Kind Cluster

The `kind-config.yaml` in the `k8s/` folder creates a cluster with port 8008 exposed on your laptop so you can open the app in the browser.

```bash
kind create cluster --config k8s/kind-config.yaml
```

This takes ~30–60 seconds. When it's done:

```bash
kubectl cluster-info --context kind-travel-ai-cluster
kubectl get nodes
```

You should see one node with status `Ready`.

---

## Step 4 — Build the Docker Image

Build the app image the same way as before. Kind needs the image to exist locally before it can use it.

```bash
docker build -t travel-ai-assistant:latest .
```

---

## Step 5 — Load the Image into Kind

Kind clusters don't have access to your local Docker images by default — you need to push the image into the cluster explicitly.

```bash
kind load docker-image travel-ai-assistant:latest --name travel-ai-cluster
```

Verify it's available inside the cluster:
```bash
docker exec -it travel-ai-cluster-control-plane crictl images | grep travel-ai
```

---

## Step 6 — Apply Kubernetes Manifests

Deploy everything with the files in the `k8s/` folder:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Or apply all at once:
```bash
kubectl apply -f k8s/
```

---

## Step 7 — Verify the Deployment

Check that the pod is running:
```bash
kubectl get pods
```

You should see something like:
```
NAME                                    READY   STATUS    RESTARTS   AGE
travel-ai-assistant-7d9f8b6c4-xk2jq   1/1     Running   0          30s
```

Check the service:
```bash
kubectl get service travel-ai-service
```

If a pod is stuck in `Pending` or `CrashLoopBackOff`, inspect it:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

---

## Step 8 — Open the App

Make sure Ollama is running on your host:
```bash
ollama serve
```

Then open your browser at:

```
http://localhost:8008
```

The port flow is: `browser:8008` → `Kind node:30080` → `pod:8008`

---

## How It All Connects

```
Your Browser (localhost:8008)
        │
        ▼
Kind Cluster (extraPortMapping: host:8008 → node:30080)
        │
        ▼
NodePort Service (30080 → 8008)
        │
        ▼
Pod: travel-ai-assistant (port 8008, uvicorn)
        │
        ▼ OLLAMA_BASE_URL=http://host.docker.internal:11434
Ollama on Host Machine (llama3.2:3b)
```

---

## Useful Commands

| Task | Command |
|------|---------|
| List all pods | `kubectl get pods` |
| View pod logs | `kubectl logs <pod-name>` |
| Describe a pod | `kubectl describe pod <pod-name>` |
| Restart deployment | `kubectl rollout restart deployment/travel-ai-assistant` |
| Delete everything | `kubectl delete -f k8s/` |
| Delete the cluster | `kind delete cluster --name travel-ai-cluster` |
| List Kind clusters | `kind get clusters` |
| Re-load image after rebuild | `kind load docker-image travel-ai-assistant:latest --name travel-ai-cluster` |

---

## Updating the App

If you change the code and want to redeploy:

```bash
# 1. Rebuild the image
docker build -t travel-ai-assistant:latest .

# 2. Reload it into Kind
kind load docker-image travel-ai-assistant:latest --name travel-ai-cluster

# 3. Restart the deployment to pick up the new image
kubectl rollout restart deployment/travel-ai-assistant

# 4. Watch it roll out
kubectl rollout status deployment/travel-ai-assistant
```

---

## Linux Note

`host.docker.internal` doesn't resolve by default on Linux. Edit `k8s/configmap.yaml` and replace:

```yaml
OLLAMA_BASE_URL: "http://host.docker.internal:11434"
```

with your host's LAN IP, e.g.:

```yaml
OLLAMA_BASE_URL: "http://192.168.1.100:11434"
```

Find your IP with: `ip route get 1 | awk '{print $7}'`
