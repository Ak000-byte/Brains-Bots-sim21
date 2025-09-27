# PING PONG 🏓

A sophisticated AI vs AI Pong environment with real-time WebSocket communication, HTTP APIs, and advanced debugging tools for training and testing intelligent paddle controllers.

## 🎯 Overview

This project provides a complete Pong game environment where AI agents can compete against each other through WebSocket and HTTP API communications. The system includes real-time ball tracking, paddle control mechanisms, scoring systems, and comprehensive debugging tools.

### ✨ Key Features

- **Dual AI Support**: Control both left (ai1) and right (ai2) paddles simultaneously
- **Multiple Control Modes**: Auto AI, Remote AI, and Human vs AI gameplay
- **Real-time Communication**: WebSocket and HTTP API endpoints for game state
- **Advanced Debugging**: Comprehensive debugging controller with detailed logging
- **Ball Physics**: Realistic ball movement with collision detection and velocity tracking
- **Score Tracking**: Persistent scoring system with API endpoints
- **Hit Detection**: Advanced ball-paddle collision detection with detailed logging

## 🚀 Quick Start

### Prerequisites

pip install websockets asyncio aiohttp

### Installation & Setup

1. **Clone the repository**:
git clone <repository-url>
cd ai-pong-environment


2. **Start the Server**:
python server.py
This launches both WebSocket (port 8765) and HTTP API (port 3000) servers.

3. **Open the Game**:
Open main.html in your browser
open main.html

4. **Configure Game Mode**:
- Select "Remote AI" mode in the game interface
- Press ENTER to start the match

5. **Run AI Controller** (Optional):
python dual_paddle_debug_controller.py

## 📁 Project Structure

ai-pong-environment/
├── main.html # Primary game interface with canvas-based Pong
├── server.py # WebSocket/HTTP server handling game state
├── dual_paddle_debug_controller.py # Advanced debugging tool for paddle control
├── HumanVsAI.html # Human vs AI game mode interface
└── README.md # Project documentation

## 🏗️ Architecture

### Core Components

- **`main.html`**: Primary game interface with canvas-based Pong implementation
- **`server.py`**: WebSocket/HTTP server handling game state and API endpoints
- **`dual_paddle_debug_controller.py`**: Advanced debugging tool for paddle control
- **`HumanVsAI.html`**: Human vs AI game mode interface

### Communication Flow

Game Interface (HTML) ←→ WebSocket Server ←→ AI Controllers
↕
HTTP API Server

## 📡 API Reference

### WebSocket Endpoints

**Connection**: `ws://localhost:8765`

#### Message Types
- **Ball Updates**: Real-time ball position and velocity data
- **Paddle Updates**: Paddle position changes
- **Score Updates**: Match score notifications
- **Game State**: Complete game state snapshots

### HTTP API Endpoints

**Base URL**: `http://localhost:3000`

#### GET Endpoints

- **`/api/ball`**: Current ball state with position and velocity
- **`/api/paddles`**: Current paddle positions for both AI agents
- **`/api/score`**: Current match scores for ai1 and ai2
- **`/api/checkpoints`**: Historical ball state data (last 50 records)

#### POST Endpoints

- **`/api/paddle-control`**: Control paddle movements
{
"paddle": "ai1",
"action": "set",
"y": 350.0

- **`/api/checkpoint-data`**: Submit ball state updates
- **`/api/score`**: Manual score updates

### Example API Usage

Get ball information
curl http://localhost:3000/api/ball

Get paddle positions
curl http://localhost:3000/api/paddles

Move ai1 paddle to position 400
curl -X POST http://localhost:3000/api/paddle-control
-H "Content-Type: application/json"
-d '{"paddle":"ai1","action":"set","y":400}'

Get current scores
curl http://localhost:3000/api/score

## 🎮 Game Modes

### 1. Auto AI Mode
- Built-in AI controls both paddles automatically
- Good for testing game mechanics without external controllers

### 2. Remote AI Mode  
- External AI scripts control paddles via WebSocket/HTTP APIs
- Primary mode for AI competitions and training

### 3. Human vs AI Mode
- Human player controls one paddle, AI controls the other
- Available through `HumanVsAI.html` interface

## 🔧 Development Tools

### Debug Controller

The dual paddle debug controller provides comprehensive testing capabilities:

python dual_paddle_debug_controller.py

**Features**:
- Tests all HTTP endpoints for connectivity
- Controls both ai1 and ai2 paddles simultaneously
- Provides detailed logging and status monitoring
- Implements ball prediction algorithms
- Supports both WebSocket and HTTP communication fallbacks

### Game Configuration

- **Canvas Dimensions**: 1400x700 pixels
- **Paddle Height**: 150 pixels
- **Default Paddle Position**: Y=350 (center)
- **Scoring**: First to 15 points wins

## 🏆 Creating AI Agents

### Basic AI Controller Template

import asyncio
import websockets
import json
import requests

class PongAI:
def init(self):
self.paddle_id = "ai1" # or "ai2"
self.api_url = "http://localhost:3000/api/paddle-control"
def calculate_target_y(self, ball_data):
    # Implement your AI logic here
    ball_x = ball_data.get('position_x', 0)
    ball_y = ball_data.get('position_y', 0)
    # Return target Y position for paddle
    return ball_y

def move_paddle(self, target_y):
    payload = {
        "paddle": self.paddle_id,
        "action": "set", 
        "y": target_y
    }
    response = requests.post(self.api_url, json=payload)
    return response.status_code == 200
Example usage in your AI script

### Advanced Features

- **Ball Prediction**: Implement trajectory prediction for better paddle positioning
- **Collision Detection**: Utilize detailed hit detection data for learning
- **Multi-Agent Training**: Control both paddles for self-play scenarios
- **Performance Monitoring**: Track response times and prediction accuracy

## 📊 Performance Tips

### AI Development Best Practices

- **Response Speed**: Aim for <100ms response times for optimal gameplay
- **Boundary Checking**: Keep paddle movements within valid Y bounds
- **Prediction Accuracy**: Use velocity data for better ball trajectory prediction
- **Error Handling**: Implement robust error handling for network communications

### Monitoring Features

The environment provides comprehensive monitoring:
- Real-time ball position and velocity tracking
- Paddle movement statistics and command success rates
- WebSocket connection status and message counts
- Hit detection accuracy and collision data

## 🤝 Contributing

This environment supports various enhancements:
- Additional game modes and difficulty levels
- Enhanced AI debugging tools and visualizations  
- Performance profiling and optimization features
- Tournament and ranking systems for AI competitions

## 📝 License

This project is designed for educational and research purposes in AI development and machine learning.

## 🐛 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**: Ensure server.py is running on port 8765
2. **Paddle Not Moving**: Check API endpoint connectivity and payload format
3. **Game Not Starting**: Verify main.html is loaded and "Remote AI" mode is selected

### Debug Steps

1. Run `dual_paddle_debug_controller.py` for comprehensive diagnostics
2. Check browser console for JavaScript errors
3. Verify HTTP API responses using curl commands
4. Monitor server.py console output for connection status

---

