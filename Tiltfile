for tf in [
    "services/ai_service/Tiltfile",
    "services/restaurant_service/Tiltfile",
    "services/booking_service/Tiltfile",
    # "services/notification_service/Tiltfile",
    # "deployment/kubernetes/rabbitmq/Tiltfile",
    "deployment/kubernetes/keycloak/Tiltfile",
    "deployment/kubernetes/kong/Tiltfile",
    
]:
    if os.path.exists(tf):
        include(tf)
