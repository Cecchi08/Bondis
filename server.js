const express = require("express");
const path = require("path");
const { exec } = require("child_process");
const cors = require("cors");

const app = express();
const port = 3002;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));
const datosRouter = require("./public/api");
app.use("/api", datosRouter);

// Ruta que ejecuta el script Python
app.get("/ejecutar-python", (req, res) => {
    const pythonPath = "python";
    const scriptPath = path.join(__dirname, "proyecto.py");

    exec(`${pythonPath} "${scriptPath}"`, (error, stdout, stderr) => {
        if (error || stderr) {
            console.error("Error ejecutando Python:", error || stderr);
            return res.json({ error: (error ? error.message : stderr) });
        }

        try {
            const data = JSON.parse(stdout);
            res.json(data);
        } catch (e) {
            console.error("Error parseando JSON:", e);
            res.json({ error: "JSON inválido desde Python" });
        }
    });
});

// Ruta principal
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Iniciar servidor
app.listen(port, () => {
    console.log(`Servidor corriendo en http://localhost:${port}`);
});
