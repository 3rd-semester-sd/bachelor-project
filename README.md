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


(Windows) Martin rebuild Lua scripts
```
k delete configmap custom-keycloak-jwt && tilt down && while kga | grep -q "pod"; do sleep 2; done && tilt up
```