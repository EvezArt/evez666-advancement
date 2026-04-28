#!/usr/bin/env python3
"""
EVEZ SENSORY NERVES - Eyes and Ears
Detects external threats to the heart (revenue, system)
"""

import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

class EvezSensoryNerves:
    """
    SENSORY SYSTEM - Detects external threats
    - EYES: Market data, dashboards, visual signals
    - EARS: News, sentiment, alerts
    """
    
    def __init__(self):
        self.sight = []  # Visual data sources
        self.hearing = []  # Audio/text data sources
        self.threat_receptors = {
            'market_crash': 0,
            'news_sentiment': 0,
            'system_health': 0,
            'revenue_drought': 0,
            'security_threat': 0
        }
        self.last_scan = None
        
        # Known threat indicators
        self.threat_keywords = [
            'hack', 'breach', 'attack', 'crash', 'fail',
            'drop', 'loss', 'decline', 'warning', 'alert'
        ]
    
    def scan_eyes(self):
        """Visual data sources - market indicators"""
        threats = []
        
        # Check market data sources (simulated)
        # In production: connect to real APIs
        threat_data = {
            'market_indicators': 'STABLE',
            'trend': 'BULL',
            'volatility': 'LOW'
        }
        
        # If volatility HIGH → threat
        if threat_data.get('volatility') == 'HIGH':
            threats.append(('market_volatility', 3))
            self.threat_receptors['market_crash'] += 2
        
        # Check system logs for visual errors
        log_files = [
            '/root/.openclaw/workspace/state/autonomous.log',
            '/root/.openclaw/workspace/state/nervous_system.log'
        ]
        
        for log_file in log_files:
            p = Path(log_file)
            if p.exists():
                content = p.read_text(errors='ignore')
                if 'error' in content.lower()[-500:]:
                    threats.append(('system_error', 2))
                    self.threat_receptors['system_health'] += 1
        
        self.sight.append({
            'timestamp': datetime.now().isoformat(),
            'threats': threats,
            'indicators': threat_data
        })
        
        return threats
    
    def scan_ears(self):
        """Audio/text sources - news, alerts"""
        threats = []
        
        # Simulated news sentiment
        # In production: connect to news API, social media
        
        news_indicators = {
            'headline': 'MARKET WATCH',
            'sentiment': 'NEUTRAL',
            'alerts': []
        }
        
        # Check for urgency in any queued messages
        
        # If negative sentiment → threat
        if news_indicators.get('sentiment') == 'BEARISH':
            threats.append(('bear_market', 4))
            self.threat_receptors['market_crash'] += 2
        
        if news_indicators.get('alerts'):
            threats.extend([(a, 2) for a in news_indicators['alerts']])
            self.threat_receptors['news_sentiment'] += 1
        
        self.hearing.append({
            'timestamp': datetime.now().isoformat(),
            'threats': threats,
            'sentiment': news_indicators.get('sentiment')
        })
        
        return threats
    
    def detect_damage(self):
        """Full threat assessment"""
        # Combine all receptors
        total_threat = 0
        
        # Market threats
        total_threat += self.threat_receptors['market_crash']
        
        # Revenue threats
        if self.threat_receptors['revenue_drought'] > 0:
            total_threat += self.threat_receptors['revenue_drought']
        
        # Security threats
        total_threat += self.threat_receptors['security_threat']
        
        # System health
        total_threat += self.threat_receptors['system_health']
        
        # Cap at 10
        total_threat = min(10, total_threat)
        
        self.last_scan = {
            'total_threat': total_threat,
            'receptors': self.threat_receptors.copy(),
            'timestamp': datetime.now().isoformat()
        }
        
        return total_threat
    
    def get_status(self):
        """Return sensory status"""
        return {
            'eyes': 'SCANNING' if self.sight else 'OFFLINE',
            'ears': 'LISTENING' if self.hearing else 'OFFLINE',
            'last_scan': self.last_scan,
            'threat_receptors': self.threat_receptors
        }


# Test
if __name__ == '__main__':
    print("=== EVEZ SENSORY NERVES ===")
    print()
    
    nerves = EvezSensoryNerves()
    
    print("1. Scanning eyes (market data)...")
    eyes_threats = nerves.scan_eyes()
    print(f"   Threats found: {eyes_threats}")
    print()
    
    print("2. Scanning ears (news/alerts)...")
    ears_threats = nerves.scan_ears()
    print(f"   Threats found: {ears_threats}")
    print()
    
    print("3. Damage assessment...")
    damage = nerves.detect_damage()
    print(f"   Total threat level: {damage}/10")
    print()
    
    print("4. Status:")
    status = nerves.get_status()
    for k, v in status.items():
        print(f"   {k}: {v}")
    
    print()
    print("=== SENSORY NERVES ONLINE ===")