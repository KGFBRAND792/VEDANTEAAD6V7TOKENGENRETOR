// ================= BACKEND: server.js ================= import express from "express"; import fetch from "node-fetch"; import path from "path";

const app = express(); const PORT = 3000;

const APP_ID = "YOUR_APP_ID"; const APP_SECRET = "YOUR_APP_SECRET"; const REDIRECT_URI = "http://localhost:3000/callback";

app.use(express.static("public"));

// Step 1: Redirect to Facebook app.get("/auth/facebook", (req, res) => { const url = https://www.facebook.com/v19.0/dialog/oauth?client_id=${APP_ID}&redirect_uri=${REDIRECT_URI}&scope=email,public_profile; res.redirect(url); });

// Step 2: Callback app.get("/callback", async (req, res) => { const code = req.query.code;

const tokenUrl = https://graph.facebook.com/v19.0/oauth/access_token?client_id=${APP_ID}&redirect_uri=${REDIRECT_URI}&client_secret=${APP_SECRET}&code=${code};

const response = await fetch(tokenUrl); const data = await response.json();

res.send(<h2>Access Token</h2> <p>${data.access_token}</p> <a href="/">Go Back</a>); });

app.listen(PORT, () => console.log(Server running on http://localhost:${PORT}));


