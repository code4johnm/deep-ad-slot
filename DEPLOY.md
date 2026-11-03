# Deploy the weekly ad scorer

One-shot CronJob. It is not a long-running service. The container scores three sites on CPU and writes one short YAML file. It does not call a language model and it does not log in to GoDaddy.

Build from the repo root so the Dockerfile can see `src/`:

```bash
cd /mnt/5TB/git/github/deep-ad-slot
docker build -f deploy/Dockerfile -t deep-ad-slot:weekly .
```

Architecture v2 (2026-11-03 15:01 ET) says only the bus listener is orchestrated by Kubernetes. Do not apply `deploy/k8s/weekly-cronjob.yaml`.

CronJob `deep-ad-slot-weekly` was applied earlier on 2026-11-03, before that order. This file does not delete it. John can remove it with:

```bash
kubectl -n default delete cronjob deep-ad-slot-weekly
```
