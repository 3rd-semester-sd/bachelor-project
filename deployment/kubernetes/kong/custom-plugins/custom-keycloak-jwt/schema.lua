return {
  name = "custom-keycloak-jwt",
  fields = {
    {
      config = {
        type = "record",
        fields = {
          { keycloak_introspection_url = { type = "string", }, },
          { client_id = { type = "string", }, },
          { client_secret = { type = "string", }, },
        },
      },
    },
  }
}
