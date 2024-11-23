import { app } from "~/app";

app.listen({ host: "0.0.0.0", port: 3000 }, (err, addr) => {
  if (err) {
    console.log(err);
    process.exit(1);
  }
});
