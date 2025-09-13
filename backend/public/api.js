const express = require("express");
const fs = require("fs");
const path = require("path");
const axios = require("axios");

const router = express.Router();

router.get("/datos", async (req, res) => {
  try {
    // Hora actual en Buenos Aires
    const currentTime = new Date().toLocaleTimeString("es-AR", {
      timeZone: "America/Argentina/Buenos_Aires",
      hour12: false,
    });

    // Leer archivo JSON de colectivos
    const colectivosPath = path.join(
      process.cwd(),
      "backend",
      "resultados_colectivos.json"
    );
    let colectivosData = {};

    if (fs.existsSync(colectivosPath)) {
      const jsonContent = fs.readFileSync(colectivosPath, "utf-8");
      try {
        colectivosData = JSON.parse(jsonContent);
      } catch {
        colectivosData = { error: "JSON de colectivos inválido o corrupto" };
      }
    } else {
      colectivosData = {
        error: "No se encontró resultados_colectivos.json",
      };
    }

    // Clima API
    const apiKey = "8ea3803heedp3nu53akbv9e93d0lo7kwzjf7w3w2"; // ⚠️ reemplazar con tu key real
    const lat = "-38.0055";
    const lon = "-57.5426";
    const weatherUrl = `https://www.meteosource.com/api/v1/free/point?lat=${lat}&lon=${lon}&sections=current&language=en&units=metric&timezone=auto&key=${apiKey}`;

    let weatherInfo = {};
    try {
      const response = await axios.get(weatherUrl, { timeout: 10000 });
      if (response.data && response.data.current) {
        weatherInfo = {
          temperature: response.data.current.temperature ?? "N/A",
          summary: response.data.current.weather ?? "N/A",
        };
      } else {
        weatherInfo = { error: "Datos de clima inválidos" };
      }
    } catch (err) {
      weatherInfo = { error: `Error API Clima: ${err.message}` };
    }

    // Respuesta final
    res.json({
      time: currentTime,
      weather: weatherInfo,
      colectivos: colectivosData,
      updated: Date.now(),
    });
  } catch (error) {
    res.status(500).json({ error: "Error interno del servidor" });
  }
});

module.exports = router;
