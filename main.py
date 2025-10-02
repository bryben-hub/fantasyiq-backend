from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FantasyIQ Pro API is live!", "status": "working"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/demo/trade")
def demo():
    return {
        "recommendation": "ACCEPT",
        "confidence": 87,
        "reasoning": "Chase youth advantage over Kelce age decline",
        "trade_details": {
            "give": ["Travis Kelce", "2025 1st"],
            "receive": ["Ja'Marr Chase"]
        },
        "value_analysis": {
            "current_value_difference": "+15%",
            "risk_level": "Low"
        }
    }

@app.get("/player/{name}")
def player(name: str):
    return {
        "name": name.title(),
        "position": "QB",
        "team": "BUF",
        "current_value": 85,
        "projections": {"2025": 88, "2026": 86, "2027": 82},
        "trend": "+3.5%",
        "recommendation": "HOLD",
        "confidence": 90,
        "reasoning": "Strong dynasty asset"
    }
