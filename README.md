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


(Windows) Mart n rebuild Lua scripts
```
k delete configmap custom-authsvc-jwt && tilt down && while kga | grep -q "pod"; do sleep 2; done && tilt up
```