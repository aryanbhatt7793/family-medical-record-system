const express = require("express");
const cors = require("cors");

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check API
app.get("/api/health", (req, res) => {
    res.json({
        status: "OK",
        message: "Family Medical Record System API is running"
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});