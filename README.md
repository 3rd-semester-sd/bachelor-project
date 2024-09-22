# Run the Project with Tilt

1. Create a K3d cluster:
   ```bash
   k3d cluster create bachelor-local -p "8080:80@loadbalancer" --registry-create bachelor-local
   ```

2. Start the project using Tilt:
   ```bash
   tilt up
   ```
