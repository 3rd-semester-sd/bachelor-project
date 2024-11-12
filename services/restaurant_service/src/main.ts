import { app } from "~/app";
import route from "./routes/restaurants";

app.listen({ port: 8000 }, (err, addr) => {
  if (err) {
    console.log(err);
    console.log("whhaaaaat");
    process.exit(1);
  }
});
