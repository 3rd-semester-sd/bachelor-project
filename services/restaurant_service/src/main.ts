import { app } from "~/app";
import route from "./routes/restaurants";

app.register(route);

app.listen({ port: 8000 }, (err, addr) => {
  console.log("err");
  if (err) {
    console.log(err);
    console.log("whhaaaaat");
    process.exit(1);
  }
});
