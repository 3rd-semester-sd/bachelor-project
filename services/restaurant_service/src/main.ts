import { app } from "~/app";

app.listen({ host: "127.0.0.1", port: 5000 }, (err, addr) => {
  if (err) {
    console.log(err);
    process.exit(1);
  }
});
