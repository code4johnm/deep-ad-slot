# Deploy the weekly ad scorer

One-shot CronJob. It is not a long-running service. The container scores three sites on CPU and writes one short YAML file. It does not call a language model and it does not log in to GoDaddy.

Build from the repo root so the Dockerfile can see `src/`:

```bash
cd /mnt/5TB/git/github/deep-ad-slot
docker build -f deploy/Dockerfile -t deep-ad-slot:weekly .
docker save deep-ad-slot:weekly | ~/bin/agent-sudo.sh k3s ctr images import -
kubectl apply -f deploy/k8s/weekly-cronjob.yaml
```

The schedule is `0 15 * * 1` (Monday 15:00, cluster local time). `imagePullPolicy` is `Never`, so the import step has to happen on this machine before the job runs.

Re-running the commands is safe. The manifest is `deploy/k8s/weekly-cronjob.yaml`. Pod `restartPolicy` is `Never`. The CronJob starts the next run.
