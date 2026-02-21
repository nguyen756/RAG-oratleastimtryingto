import dotenv from 'dotenv';
import express from 'express';
import { engine } from 'express-handlebars';
import { fileURLToPath } from 'url';


// handlebars for UI

import path from 'path';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config();
const app = express();
app.engine('handlebars', engine({
  helpers: {
    formatDate: (date) => {
      return new Date(date).toLocaleString();
    },

  }
}));
app.set('view engine', 'handlebars');
app.set('views', path.join(__dirname, 'views'));
app.use(express.urlencoded({ extended: true }));

import model_answer from "./routes/answer.route.js";
app.use("/", model_answer);

app.listen(3000, () => {
    console.log("http://localhost:3000");
});

export default app;
