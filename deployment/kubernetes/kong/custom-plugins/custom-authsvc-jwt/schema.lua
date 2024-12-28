return {
  name = "custom-authsvc-jwt",
  fields = {
    {
      config = {
        type = "record",
        fields = {
          { current_user_url = { type = "string", }, },
        },
      },
    },
  }
}
