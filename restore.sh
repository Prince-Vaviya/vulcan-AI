#!/bin/bash

# Re-apply configurations using kubectl apply -f kubernetes/
echo "Restoring Kubernetes configurations..."
kubectl apply -f kubernetes/

echo "Disaster recovery restore complete!"