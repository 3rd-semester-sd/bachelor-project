return {
  name = "custom-keycloak-jwt",
  fields = {
    { config = {
        type = "record",
        fields = {
          { keycloak_introspection_url = { type = "string", default = "roar", }, },
          { client_id = { type = "string", default = "roar", }, },
          { client_secret = { type = "string", default = "roar", }, },
        },
    }, },
  }
}