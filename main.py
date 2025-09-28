# main.py - FantasyIQ Pro Backend - FIXED VERSION
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from datetime import datetime
import json

# Initialize FastAPI
app = FastAPI(title="FantasyIQ Pro API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Data Models
class PlayerAnalysisRequest(BaseModel):
    player_name: str
    position: str
    team: str
    age: Optional[int] = None

class TradeAnalysisRequest(BaseModel):
    give_players: List[str]
    receive_players: List[str]
    league_type: str = "dynasty"

class PlayerResponse(BaseModel):
    name: str
    position: str
    team: str
    current_value: int
    projections: dict
    trend: str
    recommendation: str
    confidence: int

# Mock Database - Pre-loaded with top dynasty players
MOCK_PLAYERS = {
    "josh allen": {
        "name": "Josh Allen",
        "position": "QB",
        "team": "BUF",
        "current_value": 85,
        "projections": {"2025": 88, "2026": 86, "2027": 82},
        "trend": "+3.5%",
        "recommendation": "HOLD",
        "confidence": 92,
        "reasoning": "Elite dual-threat QB entering prime years. Consistent top-5 fantasy performer with rushing upside."
    },
    "lamar jackson": {
        "name": "Lamar Jackson",
        "position": "QB", 
        "team": "BAL",
        "current_value": 82,
        "projections": {"2025": 84, "2026": 80, "2027": 75},
        "trend": "+2.4%",
        "recommendation": "HOLD",
        "confidence": 87,
        "reasoning": "Unique rushing ability with improved passing. Age 27 sweet spot for dynasty value."
    },
    "ja'marr chase": {
        "name": "Ja'Marr Chase",
        "position": "WR",
        "team": "CIN",
        "current_value": 92,
        "projections": {"2025": 94, "2026": 93, "2027": 89},
        "trend": "+2.2%",
        "recommendation": "BUY",
        "confidence": 95,
        "reasoning": "Elite young WR1 with top-tier QB. Age 24 with 8+ years of WR1 upside remaining."
    },
    "ceedee lamb": {
        "name": "CeeDee Lamb",
        "position": "WR",
        "team": "DAL", 
        "current_value": 88,
        "projections": {"2025": 90, "2026": 89, "2027": 85},
        "trend": "+2.3%",
        "recommendation": "BUY",
        "confidence": 89,
        "reasoning": "Proven WR1 with elite target share. Strong QB play and offensive system support long-term value."
    },
    "amon-ra st. brown": {
        "name": "Amon-Ra St. Brown",
        "position": "WR",
        "team": "DET",
        "current_value": 78,
        "projections": {"2025": 82, "2026": 84, "2027": 80},
        "trend": "+5.1%",
        "recommendation": "BUY LOW",
        "confidence": 83,
        "reasoning": "Ascending WR2 with WR1 upside. Lions offense improving, target share increasing each season."
    },
    "breece hall": {
        "name": "Breece Hall",
        "position": "RB",
        "team": "NYJ",
        "current_value": 78,
        "projections": {"2025": 85, "2026": 88, "2027": 82},
        "trend": "+8.9%",
        "recommendation": "BUY LOW",
        "confidence": 85,
        "reasoning": "Elite talent returning from injury. Young age and improved Jets offense create massive upside."
    },
    "bijan robinson": {
        "name": "Bijan Robinson", 
        "position": "RB",
        "team": "ATL",
        "current_value": 82,
        "projections": {"2025": 86, "2026": 87, "2027": 83},
        "trend": "+4.9%",
        "recommendation": "BUY",
        "confidence": 88,
        "reasoning": "Generational RB talent with 3-down skill set. Age 22 with long-term RB1 ceiling."
    },
    "travis kelce": {
        "name": "Travis Kelce",
        "position": "TE", 
        "team": "KC",
        "current_value": 89,
        "projections": {"2025": 84, "2026": 78, "2027": 70},
        "trend": "-5.6%",
        "recommendation": "SELL HIGH",
        "confidence": 91,
        "reasoning": "Age 35 with declining athleticism. Elite but aging asset - sell to contender before regression."
    },
    "mark andrews": {
        "name": "Mark Andrews",
        "position": "TE",
        "team": "BAL", 
        "current_value": 76,
        "projections": {"2025": 78, "2026": 75, "2027": 70},
        "trend": "+2.6%",
        "recommendation": "HOLD",
        "confidence": 79,
        "reasoning": "Consistent TE1 with strong QB connection. Age concerns but proven red zone target."
    },
    "sam laporta": {
        "name": "Sam LaPorta",
        "position": "TE",
        "team": "DET",
        "current_value": 74,
        "projections": {"2025": 78, "2026": 82, "2027": 84},
        "trend": "+5.4%",
        "recommendation": "BUY LOW",
        "confidence": 86,
        "reasoning": "Breakout rookie season indicates elite potential. Young age with ascending Lions offense."
    }
}

def get_ai_analysis(prompt: str) -> str:
    """Get AI analysis from OpenAI"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert fantasy football dynasty analyst. Provide concise, actionable insights in 2-3 sentences."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "AI analysis temporarily unavailable. Consider player age, recent performance, and team situation for dynasty value."

@app.get("/")
def read_root():
    return {
        "message": "FantasyIQ Pro API is live! 🚀", 
        "version": "1.0.0",
        "status": "Ready for dynasty domination"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "players_loaded": len(MOCK_PLAYERS)
    }

@app.get("/player/{player_name}")
def get_player_analysis(player_name: str):
    """Get AI-powered player analysis"""
    
    # Normalize player name for lookup
    player_key = player_name.lower().replace("'", "").replace(".", "").replace("-", "-")
    
    # Check mock database first
    if player_key in MOCK_PLAYERS:
        player = MOCK_PLAYERS[player_key]
        return {
            **player,
            "analysis_type": "comprehensive",
            "last_updated": datetime.now().isoformat()
        }
    
    # Generate AI analysis for unknown players
    prompt = f"""
    Analyze {player_name} for dynasty fantasy football:
    
    Provide:
    1. Current dynasty value (0-100 scale)
    2. 2025, 2026, 2027 fantasy projections (0-100 scale)
    3. Buy/Sell/Hold recommendation with reasoning
    4. Confidence level (0-100%)
    
    Focus on age, talent, team situation, and dynasty outlook.
    """
    
    ai_analysis = get_ai_analysis(prompt)
    
    return {
        "name": player_name.title(),
        "position": "Unknown",
        "team": "UNK", 
        "current_value": 72,
        "projections": {"2025": 74, "2026": 72, "2027": 68},
        "trend": "±2%",
        "recommendation": "RESEARCH",
        "confidence": 65,
        "reasoning": ai_analysis,
        "analysis_type": "ai_generated",
        "last_updated": datetime.now().isoformat()
    }

@app.post("/trade/analyze")
def analyze_trade(trade: TradeAnalysisRequest):
    """Analyze a dynasty trade using AI"""
    
    prompt = f"""
    Analyze this dynasty fantasy football trade:
    
    Team A Gives: {', '.join(trade.give_players)}
    Team A Receives: {', '.join(trade.receive_players)}
    
    Consider:
    - Current vs future value
    - Age curves and longevity  
    - Position scarcity
    - Team contexts and situations
    
    Provide:
    - Recommendation: ACCEPT, REJECT, or NEUTRAL
    - Confidence percentage (0-100%)
    - Brief reasoning (2-3 sentences)
    """
    
    ai_analysis = get_ai_analysis(prompt)
    
    # Simple heuristic for demo
    give_count = len(trade.give_players)
    receive_count = len(trade.receive_players)
    
    # Basic recommendation logic
    if "1st" in str(trade.receive_players) and receive_count >= give_count:
        recommendation = "ACCEPT"
        confidence = 82
    elif any(name.lower() in ["kelce", "henry", "jones"] for name in trade.give_players):
        recommendation = "ACCEPT" 
        confidence = 78
    elif give_count > receive_count:
        recommendation = "REJECT"
        confidence = 71
    else:
        recommendation = "NEUTRAL"
        confidence = 68
    
    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "reasoning": ai_analysis,
        "trade_details": {
            "give": trade.give_players,
            "receive": trade.receive_players,
            "league_type": trade.league_type
        },
        "value_analysis": {
            "current_value_difference": f"{((receive_count - give_count) * 10):+d}%",
            "long_term_outlook": "Positive" if recommendation == "ACCEPT" else "Neutral",
            "risk_level": "Medium"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/insights/weekly")
def get_weekly_insights(tier: str = "free"):
    """Get weekly AI insights based on subscription tier"""
    
    base_insights = [
        {
            "type": "buy_low",
            "player": "Breece Hall",
            "content": "Injury concerns creating excellent buying opportunity. Expected return to RB1 status with improved Jets offense.",
            "confidence": 85,
            "priority": "high"
        },
        {
            "type": "sell_high", 
            "player": "Travis Kelce",
            "content": "Peak value window closing rapidly. Age 35 regression likely starting 2025 season.",
            "confidence": 91,
            "priority": "urgent"
        },
        {
            "type": "sleeper",
            "player": "Sam LaPorta",
            "content": "Breakout TE performance indicates long-term TE1 ceiling. Buy before price increases.",
            "confidence": 86,
            "priority": "medium"
        }
    ]
    
    if tier == "free":
        return {
            "insights": base_insights[:2],  # Only 2 for free users
            "upgrade_message": "Upgrade to Pro for 15+ weekly insights + trade alerts",
            "total_available": 18,
            "tier": "free"
        }
    
    # Pro tier gets all insights
    pro_insights = base_insights + [
        {
            "type": "breakout",
            "player": "Amon-Ra St. Brown", 
            "content": "Lions offensive explosion makes him weekly WR1 candidate. Age 24 with 5+ elite years ahead.",
            "confidence": 83,
            "priority": "medium"
        },
        {
            "type": "bust_alert",
            "player": "DeAndre Hopkins",
            "content": "Age 32 with declining separation. Sell to contender before value craters further.",
            "confidence": 78,
            "priority": "medium"
        },
        {
            "type": "rookie_watch",
            "player": "Rome Odunze",
            "content": "Bears offense improvement trajectory makes him 2026 WR2+ candidate with Caleb Williams development.",
            "confidence": 74,
            "priority": "low"
        }
    ]
    
    return {
        "insights": pro_insights,
        "tier": tier,
        "total_insights": len(pro_insights),
        "updated": datetime.now().isoformat()
    }

@app.get("/players/search")
def search_players(q: str):
    """Search for players in database"""
    query = q.lower().replace("'", "").replace(".", "")
    results = []
    
    for key, player in MOCK_PLAYERS.items():
        if query in key or query in player["name"].lower():
            results.append({
                "name": player["name"],
                "position": player["position"], 
                "team": player["team"],
                "value": player["current_value"],
                "trend": player["trend"],
                "recommendation": player["recommendation"]
            })
    
    return {
        "results": results, 
        "query": q,
        "total_found": len(results)
    }

@app.get("/trending")
def get_trending_players():
    """Get trending dynasty players"""
    
    # Sort by trend percentage
    trending = []
    for player in MOCK_PLAYERS.values():
        trend_num = float(player["trend"].replace("%", "").replace("+", ""))
        trending.append({
            **player,
            "trend_numeric": trend_num
        })
    
    # Sort by trend
    trending.sort(key=lambda x: x["trend_numeric"], reverse=True)
    
    return {
        "trending_up": trending[:3],
        "trending_down": trending[-3:],
        "updated": datetime.now().isoformat()
    }

@app.get("/demo/trade")
def demo_trade_analysis():
    """Demo trade for showcasing the tool - FIXED VERSION"""
    
    return {
        "recommendation": "ACCEPT",
        "confidence": 87,
        "reasoning": "Ja'Marr Chase's youth (24) and elite WR1 ceiling outweigh Kelce's aging curve (35). The 2025 1st is valuable, but Chase provides 5+ years of WR1 production vs. Kelce's 2-3 years of declining TE1 value.",
        "trade_details": {
            "give": ["Travis Kelce", "2025 1st Round Pick"],
            "receive": ["Ja'Marr Chase"],
            "league_type": "dynasty"
        },
        "value_analysis": {
            "current_value_difference": "+15%",
            "projected_2027_difference": "+35%", 
            "risk_level": "Low",
            "age_advantage": "Chase: 24 vs Kelce: 35"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000))))))
