# Run the Project with Tilt

1. Create a K3d cluster:
   ```bash
   k3d cluster create bachelor-local --registry-create bachelor-local
   ```

2. Start the project using Tilt:
   ```bash
   tilt up
   ```

3. Delete the Kubernetes objects:
   ```bash
   tilt down
   ```


(Windows) Martin rebuild plugin Lua scripts
```
k delete configmap custom-authsvc-jwt && tilt down && while kga | grep -q "pod"; do sleep 2; done && tilt up
```

(Azure) get the kubeconfig
```
az aks get-credentials --resource-group $RESOURCE_GROUP_NAME --name $CLUSTER_NAME
az aks get-credentials --resource-group rg-terraform-dev  --name aks-terraform-dev
```

(Docker) build and push images
```bash
cd services/x
docker build -t mslaursen/x-service:x.x .
docker push mslaursen/x-service:x.x

# or use this script (replace values as needed)
./build_and_push.sh mslaursen 0.1
./build_and_push.sh mslaursen 0.1 notification_service
```

(Terraform) deploy all infrastructure
```bash
cd deployment/terraform/dev
terraform init
terraform apply
```

(Kubernetes) install the services into the deployed AKS cluster
```bash
helm install ai-release deployment/charts/base -f deployment/kubernetes/ai_service/values.dev.yaml
helm install auth-release deployment/charts/base -f deployment/kubernetes/auth_service/values.dev.yaml
helm install booking-release deployment/charts/base -f deployment/kubernetes/booking_service/values.dev.yaml
helm install notification-release deployment/charts/base -f deployment/kubernetes/notification_service/values.dev.yaml
helm install restaurant-release deployment/charts/base -f deployment/kubernetes/restaurant_service/values.dev.yaml

# kong
kubectl create configmap custom-authsvc-jwt --from-file=deployment/kubernetes/kong/custom-plugins/custom-authsvc-jwt
helm install kong kong/kong -f deployment/kubernetes/kong/values.dev.yaml
kubectl apply -f deployment/kubernetes/kong/ingress.yaml
kubectl apply -f deployment/kubernetes/kong/plugins.yaml

# bitnami
helm repo add bitnami https://charts.bitnami.com/bitnami
-
# rabbitmq
helm install rabbitmq bitnami/rabbitmq -f deployment/kubernetes/rabbitmq/values.yaml

# redis
helm install redis bitnami/redis -f deployment/kubernetes/redis/values.dev.yaml

# elasticsearch
helm install elasticsearch bitnami/elasticsearch -f deployment/kubernetes/elasticsearch/values.dev.yaml
```
