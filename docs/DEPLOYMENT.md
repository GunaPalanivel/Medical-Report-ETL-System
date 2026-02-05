# Deployment Guide

**Production deployment, monitoring, and operations.**

---

## Pre-Deployment Checklist

Before going to production:

- [ ] 85%+ test coverage passing
- [ ] Code reviewed by 2+ developers
- [ ] HIPAA compliance verified
- [ ] Encryption keys generated & stored
- [ ] Backup strategy defined
- [ ] Monitoring & alerting configured
- [ ] Disaster recovery plan documented
- [ ] Staff trained on operations
- [ ] Audit logging enabled
- [ ] Data retention policy set

---

## Deployment Environments

### Development (Local)

```bash
# .env
ENV=development
LOG_LEVEL=DEBUG
WORKERS=1
ENCRYPTION_ENABLED=false
VALIDATION_MODE=lenient
```

**Use Case:** Feature development, testing

### Staging (Pre-Production)

```bash
# .env
ENV=staging
LOG_LEVEL=INFO
WORKERS=2
ENCRYPTION_ENABLED=true
VALIDATION_MODE=strict
```

**Use Case:** Integration testing, performance testing, compliance verification

### Production

```bash
# .env
ENV=production
LOG_LEVEL=WARNING
WORKERS=4
ENCRYPTION_ENABLED=true
VALIDATION_MODE=strict
BACKUP_ENABLED=true
MONITORING_ENABLED=true
```

**Use Case:** Live data processing, must be highly available

---

## Docker Deployment

### Build & Push Image

```bash
# Build image
docker build -t medical-etl:v1.0.0 .

# Tag for registry (AWS ECR example)
docker tag medical-etl:v1.0.0 123456789.dkr.ecr.us-east-1.amazonaws.com/medical-etl:v1.0.0

# Push to registry
aws ecr get-login-password | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/medical-etl:v1.0.0
```

### Docker Compose (Single Host)

```yaml
# docker-compose.yml
version: "3.8"

services:
  medical-etl:
    build: .
    container_name: medical-etl-service
    environment:
      ENV: production
      WORKERS: 4
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
      LOG_LEVEL: INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    ports:
      - "8000:8000" # Metrics endpoint (Phase 6)
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Optional: Prometheus monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
    ports:
      - "9090:9090"
    restart: always

volumes:
  prometheus_data:
```

**Run:**

```bash
docker-compose up -d
docker-compose logs -f medical-etl
docker-compose stop
```

### Kubernetes Deployment (High Availability)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: medical-etl
  namespace: production
spec:
  replicas: 3 # 3 instances for HA
  selector:
    matchLabels:
      app: medical-etl
  template:
    metadata:
      labels:
        app: medical-etl
    spec:
      containers:
        - name: medical-etl
          image: 123456789.dkr.ecr.us-east-1.amazonaws.com/medical-etl:v1.0.0
          env:
            - name: ENV
              value: "production"
            - name: WORKERS
              value: "4"
            - name: ENCRYPTION_KEY
              valueFrom:
                secretKeyRef:
                  name: etl-secrets
                  key: encryption-key
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "2"
          volumeMounts:
            - name: data-volume
              mountPath: /app/data
            - name: logs-volume
              mountPath: /app/logs
          livenessProbe:
            httpGet:
              path: /metrics
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
      volumes:
        - name: data-volume
          persistentVolumeClaim:
            claimName: medical-etl-data
        - name: logs-volume
          persistentVolumeClaim:
            claimName: medical-etl-logs
```

**Deploy:**

```bash
# Create secrets
kubectl create secret generic etl-secrets \
  --from-literal=encryption-key=$ENCRYPTION_KEY \
  -n production

# Apply deployment
kubectl apply -f k8s/

# Check status
kubectl get pods -n production
kubectl logs -f deployment/medical-etl -n production
```

---

## Cloud Deployment

### AWS ECS (Elastic Container Service)

```bash
# Create task definition
aws ecs register-task-definition \
  --family medical-etl \
  --requires-compatibilities FARGATE \
  --network-mode awsvpc \
  --cpu 2048 \
  --memory 4096 \
  --container-definitions file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster production \
  --service-name medical-etl \
  --task-definition medical-etl \
  --desired-count 3 \
  --launch-type FARGATE
```

### Google Cloud Run

```bash
# Deploy container
gcloud run deploy medical-etl \
  --image gcr.io/my-project/medical-etl:v1.0.0 \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 3600 \
  --set-env-vars ENV=production,WORKERS=4
```

### Azure Container Instances

```bash
# Create container group
az container create \
  --resource-group medical-etl-rg \
  --name medical-etl \
  --image myregistry.azurecr.io/medical-etl:v1.0.0 \
  --memory 2 \
  --cpu 2 \
  --restart-policy Always
```

---

## Monitoring & Alerting

### Prometheus Metrics (Phase 6)

```yaml
# monitoring/prometheus.yml
scrape_configs:
  - job_name: "medical-etl"
    static_configs:
      - targets: ["localhost:8000"]
    scrape_interval: 30s
```

**Key Metrics:**

```
# Processing throughput
rate(pdf_processed_total[5m])

# Error rate
rate(pdf_errors_total[5m]) / rate(pdf_processed_total[5m])

# Processing latency (p95)
histogram_quantile(0.95, process_duration_seconds_bucket)

# Memory usage
memory_usage_bytes

# Queue depth
queue_depth_items
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Medical ETL Pipeline",
    "panels": [
      {
        "title": "Throughput (PDFs/min)",
        "targets": [{ "expr": "rate(pdf_processed_total[5m]) * 60" }]
      },
      {
        "title": "Error Rate (%)",
        "targets": [
          {
            "expr": "rate(pdf_errors_total[5m]) / rate(pdf_processed_total[5m]) * 100"
          }
        ]
      },
      {
        "title": "Processing Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, process_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Memory Usage (MB)",
        "targets": [{ "expr": "memory_usage_bytes / 1e6" }]
      }
    ]
  }
}
```

### Alerting Rules

```yaml
# monitoring/alerts.yaml
groups:
  - name: medical-etl
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(pdf_errors_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "ETL error rate > 5%"
          severity: critical

      - alert: HighProcessingLatency
        expr: histogram_quantile(0.95, process_duration_seconds_bucket) > 2
        for: 5m
        annotations:
          summary: "Processing latency (p95) > 2s"
          severity: warning

      - alert: HighMemoryUsage
        expr: memory_usage_bytes > 2e9
        for: 10m
        annotations:
          summary: "Memory usage > 2GB"
          severity: warning

      - alert: QueueBacklog
        expr: queue_depth_items > 1000
        for: 5m
        annotations:
          summary: "Processing queue > 1000 items"
          severity: warning
```

---

## Backup & Recovery

### Daily Backup Strategy

```bash
#!/bin/bash
# backup.sh
set -e

# Backup directory structure
BACKUP_DIR="/backups/medical-etl/$(date +%Y-%m-%d)"
mkdir -p $BACKUP_DIR

# Backup anonymized reports
tar -czf $BACKUP_DIR/anonymized_reports.tar.gz data/anonymized_reports/

# Backup metadata (with encryption)
gpg --symmetric --cipher-algo AES256 data/patient_metadata.json
mv data/patient_metadata.json.gpg $BACKUP_DIR/

# Backup ID map (encrypted)
gpg --symmetric --cipher-algo AES256 data/id_map.json
mv data/id_map.json.gpg $BACKUP_DIR/

# Backup logs
tar -czf $BACKUP_DIR/logs.tar.gz logs/

# Upload to cloud
aws s3 sync $BACKUP_DIR s3://medical-etl-backups/$(date +%Y-%m-%d)/

# Cleanup old backups (7-year retention)
find /backups/medical-etl -type f -mtime +2555 -delete

echo "Backup completed: $BACKUP_DIR"
```

**Schedule with cron:**

```bash
# Backup daily at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/medical-etl-backup.log 2>&1
```

### Recovery Procedure

```bash
# 1. List available backups
ls -la /backups/medical-etl/

# 2. Restore from specific date
BACKUP_DATE=2026-02-05
aws s3 sync s3://medical-etl-backups/$BACKUP_DATE .

# 3. Restore files
tar -xzf anonymized_reports.tar.gz -C data/
gpg --decrypt patient_metadata.json.gpg > data/patient_metadata.json
gpg --decrypt id_map.json.gpg > data/id_map.json
tar -xzf logs.tar.gz

# 4. Verify integrity
# Check file counts, log entries, etc

# 5. Resume operations
docker-compose up -d
```

---

## Health Checks

### Liveness Probe

```python
# src/health/liveness.py
from flask import Flask

app = Flask(__name__)

@app.route('/health/live')
def liveness():
    """Is the service running?"""
    return {'status': 'alive'}, 200
```

### Readiness Probe

```python
@app.route('/health/ready')
def readiness():
    """Is the service ready to accept requests?"""
    checks = {
        'database': check_db_connection(),
        'storage': check_storage_access(),
        'encryption': check_encryption_key(),
    }

    if all(checks.values()):
        return {'status': 'ready', 'checks': checks}, 200
    else:
        return {'status': 'not ready', 'checks': checks}, 503

def check_db_connection():
    try:
        # Attempt database query
        return True
    except:
        return False

def check_storage_access():
    try:
        # Check read/write to storage
        Path('data/raw_reports').mkdir(exist_ok=True)
        return True
    except:
        return False

def check_encryption_key():
    try:
        key = os.getenv('ENCRYPTION_KEY')
        Fernet(key)
        return True
    except:
        return False
```

**Kubernetes Probes:**

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

---

## Scaling

### Horizontal Scaling

```bash
# If using Docker Compose
docker-compose up -d --scale medical-etl=3

# If using Kubernetes
kubectl scale deployment medical-etl --replicas=3 -n production

# If using AWS ECS
aws ecs update-service \
  --cluster production \
  --service medical-etl \
  --desired-count 5
```

### Auto-Scaling Rules

```yaml
# k8s/hpa.yaml (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: medical-etl-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: medical-etl
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## Troubleshooting Production Issues

### High Error Rate

```bash
# Check logs
docker logs medical-etl | grep ERROR | tail -20

# Check metrics
curl http://localhost:8000/metrics | grep error

# Scale up if processing queue is high
docker-compose up -d --scale medical-etl=5
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean old logs
find logs/ -mtime +7 -delete

# Verify backups are synced to cloud, then delete local
rm -rf /backups/medical-etl/2020-*
```

### Memory Leak

```bash
# Monitor memory over time
docker stats --no-stream

# Restart container to reclaim memory
docker-compose restart medical-etl

# Investigate with memory profiler
pip install memory-profiler
python -m memory_profiler main.py
```

---

## Operations Checklist

**Daily:**

- [ ] Check error rate < 5%
- [ ] Monitor queue depth
- [ ] Verify backup completion

**Weekly:**

- [ ] Review audit logs for anomalies
- [ ] Check disk usage
- [ ] Update dependencies if security patches available

**Monthly:**

- [ ] Test disaster recovery procedure
- [ ] Review and update alerting rules
- [ ] Analyze performance trends

**Quarterly:**

- [ ] Rotate encryption keys
- [ ] Conduct security audit
- [ ] User access review

**Annually:**

- [ ] HIPAA compliance audit
- [ ] Penetration testing
- [ ] Capacity planning

---

## Next Steps

- 🚀 Ready to deploy? Start with [Docker Setup](#docker-deployment)
- 📊 Setup monitoring? See Prometheus section above
- 🔐 Secure your keys? Use AWS Secrets Manager or Kubernetes Secrets
