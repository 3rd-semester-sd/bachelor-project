load("ext://helm_resource", "helm_resource", "helm_repo")

helm_repo(name="bitnami", url="https://charts.bitnami.com/bitnami")

for tf in [
    #"services/ai_service/Tiltfile",
    #"services/restaurant_service/Tiltfile",
    #"services/booking_service/Tiltfile",
    "services/notification_service/Tiltfile",
    "services/auth_service/Tiltfile",
    "deployment/kubernetes/rabbitmq/Tiltfile",
    #"deployment/kubernetes/redis/Tiltfile",
    #"deployment/kubernetes/keycloak/Tiltfile",
    "deployment/kubernetes/kong/Tiltfile",
    
]:
    if os.path.exists(tf):
        include(tf)
