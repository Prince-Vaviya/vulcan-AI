#!/bin/bash

# Export the active Kubernetes state
echo "Exporting active Kubernetes state to backup.txt..."
kubectl get all -A > backup.txt

# Compress configurations into a tar archive
echo "Packaging Kubernetes configurations into kubernetes-config-backup.tar.gz..."
tar -czf kubernetes-config-backup.tar.gz kubernetes/

echo "Disaster recovery backup complete!"