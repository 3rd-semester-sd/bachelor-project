import { app } from "~/app";
import route from "./routes/restaurants";

app.listen({ port: 5000 }, (err, addr) => {
  if (err) {
    console.log(err);
    process.exit(1);
  }
});
