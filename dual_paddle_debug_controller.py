#!/usr/bin/env python3

"""

DUAL PADDLE DEBUG CONTROLLER - Both AI Paddles Working Together

This enhanced controller will:

1. Control BOTH paddle_ai1 (left) and paddle_ai2 (right) simultaneously
2. Test all API endpoints for both paddles
3. Send paddle movements using multiple methods for both sides
4. Show detailed debugging information for both paddles
5. Fix paddle movement issues in remote AI mode for both paddles

"""

import asyncio
import websockets
import json
import requests
import time
import threading
from typing import Dict, Optional

class DualPaddleDebugController:
    """
    Enhanced debug controller to fix paddle movement issues for BOTH AI paddles
    """

    def __init__(self):
        # Server endpoints (based on code analysis)
        self.ws_host = "localhost"
        self.ws_port = 8765
        self.http_host = "localhost"
        self.http_port = 3000

        # Game state
        self.canvas_height = 700
        self.canvas_width = 1400
        self.paddle_height = 150 # From main.html analysis

        # Paddle states - tracking both paddles
        self.paddle_states = {
            "ai1": {
                "current_y": 350.0,
                "commands_sent": 0,
                "paddle_x": 50,  # Left paddle
                "name": "LEFT (AI1)"
            },
            "ai2": {
                "current_y": 350.0,
                "commands_sent": 0,
                "paddle_x": 1350,  # Right paddle (canvas_width - 50)
                "name": "RIGHT (AI2)"
            }
        }

        # Debug tracking
        self.messages_received = 0
        self.websocket_connected = False
        self.last_ball_data = None

        print(f"🔧 DUAL PADDLE DEBUG Controller initialized")
        print(f"🎮 Controlling BOTH paddles: ai1 (LEFT) and ai2 (RIGHT)")
        print(f"🌐 HTTP API: http://{self.http_host}:{self.http_port}")
        print(f"📡 WebSocket: ws://{self.ws_host}:{self.ws_port}")

    def test_http_endpoints(self):
        """Test all HTTP endpoints to verify they work for both paddles"""
        print("\n🧪 TESTING HTTP ENDPOINTS FOR BOTH PADDLES")
        print("=" * 60)

        # Test 1: GET /api/ball
        try:
            url = f"http://{self.http_host}:{self.http_port}/api/ball"
            response = requests.get(url, timeout=2)
            print(f"📍 GET /api/ball: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Ball data: {data}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ GET /api/ball failed: {e}")

        # Test 2: GET /api/paddles
        try:
            url = f"http://{self.http_host}:{self.http_port}/api/paddles"
            response = requests.get(url, timeout=2)
            print(f"🏓 GET /api/paddles: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Paddle data: {data}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ GET /api/paddles failed: {e}")

        # Test 3: POST /api/paddle-control for BOTH paddles
        for paddle_id in ["ai1", "ai2"]:
            paddle_name = self.paddle_states[paddle_id]["name"]
            try:
                url = f"http://{self.http_host}:{self.http_port}/api/paddle-control"
                payload = {
                    "paddle": paddle_id,
                    "action": "set",
                    "y": 400.0  # Test position
                }

                response = requests.post(url, json=payload, timeout=2)
                print(f"🎮 POST /api/paddle-control ({paddle_name}): {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ {paddle_name} control SUCCESS: {data}")
                    self.paddle_states[paddle_id]["commands_sent"] += 1
                else:
                    print(f"   ❌ {paddle_name} control FAILED: {response.text}")
            except Exception as e:
                print(f"❌ POST /api/paddle-control ({paddle_name}) failed: {e}")

        # Test 4: GET /api/score
        try:
            url = f"http://{self.http_host}:{self.http_port}/api/score"
            response = requests.get(url, timeout=2)
            print(f"📊 GET /api/score: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Score data: {data}")
        except Exception as e:
            print(f"❌ GET /api/score failed: {e}")

    def send_paddle_command_http(self, paddle_id: str, target_y: float) -> bool:
        """Send paddle command via HTTP API for specified paddle"""
        try:
            url = f"http://{self.http_host}:{self.http_port}/api/paddle-control"
            payload = {
                "paddle": paddle_id,
                "action": "set",
                "y": float(target_y)
            }

            response = requests.post(url,
                                   json=payload,
                                   headers={"Content-Type": "application/json"},
                                   timeout=0.1)

            if response.status_code == 200:
                self.paddle_states[paddle_id]["commands_sent"] += 1
                self.paddle_states[paddle_id]["current_y"] = target_y
                paddle_name = self.paddle_states[paddle_id]["name"]
                print(f"✅ HTTP {paddle_name} moved to {target_y:.1f}")
                return True
            else:
                paddle_name = self.paddle_states[paddle_id]["name"]
                print(f"❌ HTTP {paddle_name} command failed: {response.status_code}")
                return False
        except Exception as e:
            paddle_name = self.paddle_states[paddle_id]["name"]
            print(f"⚠️ HTTP {paddle_name} error: {e}")
            return False

    async def send_paddle_command_websocket(self, websocket, paddle_id: str, target_y: float) -> bool:
        """Send paddle command via WebSocket for specified paddle"""
        try:
            # Method 1: Send as paddleupdate message (matching main.html format)
            paddle_update = {
                "type": "paddleupdate",
                "paddle": paddle_id,
                "y": float(target_y),
                "timestamp": time.time() * 1000
            }

            await websocket.send(json.dumps(paddle_update))
            paddle_name = self.paddle_states[paddle_id]["name"]
            print(f"📡 WS {paddle_name} update sent: {target_y:.1f}")
            return True
        except Exception as e:
            paddle_name = self.paddle_states[paddle_id]["name"]
            print(f"⚠️ WS {paddle_name} error: {e}")
            return False

    def calculate_target_position(self, ball_data: Dict, paddle_id: str) -> float:
        """Calculate where paddle should move based on ball position"""
        try:
            # Extract ball position
            ball_x = float(ball_data.get('position_x', ball_data.get('x', self.canvas_width/2)))
            ball_y = float(ball_data.get('position_y', ball_data.get('y', self.canvas_height/2)))
            ball_vx = float(ball_data.get('velocity_x', ball_data.get('velocityX', 0)))
            ball_vy = float(ball_data.get('velocity_y', ball_data.get('velocityY', 0)))

            # Get paddle position and determine direction
            paddle_x = self.paddle_states[paddle_id]["paddle_x"]
            paddle_name = self.paddle_states[paddle_id]["name"]

            # Determine if ball is moving toward this paddle
            moving_toward_us = (paddle_id == "ai1" and ball_vx < 0) or (paddle_id == "ai2" and ball_vx > 0)

            if not moving_toward_us:
                # Ball moving away - return center position
                return self.canvas_height / 2

            # Simple prediction: where will ball be when it reaches paddle
            if abs(ball_vx) > 1:
                time_to_paddle = abs(paddle_x - ball_x) / abs(ball_vx)
                predicted_y = ball_y + (ball_vy * time_to_paddle)

                # Handle wall bounces (simple version)
                while predicted_y < 0 or predicted_y > self.canvas_height:
                    if predicted_y < 0:
                        predicted_y = -predicted_y
                    elif predicted_y > self.canvas_height:
                        predicted_y = 2 * self.canvas_height - predicted_y

                # Ensure within paddle bounds
                min_y = self.paddle_height / 2 + 25
                max_y = self.canvas_height - self.paddle_height / 2 - 25
                target_y = max(min_y, min(max_y, predicted_y))

                print(f"🎯 {paddle_name}: Ball at ({ball_x:.0f},{ball_y:.0f}), vel=({ball_vx:.1f},{ball_vy:.1f}) -> Target: {target_y:.0f}")
                return target_y
            else:
                # Ball too slow, just track its Y position
                return max(self.paddle_height/2 + 25,
                          min(self.canvas_height - self.paddle_height/2 - 25, ball_y))

        except Exception as e:
            paddle_name = self.paddle_states[paddle_id]["name"]
            print(f"⚠️ {paddle_name} target calculation error: {e}")
            return self.canvas_height / 2

    async def websocket_main_loop(self):
        """Main WebSocket connection and message handling loop"""
        print("\n📡 STARTING WEBSOCKET CONNECTION")
        print("=" * 50)

        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                uri = f"ws://{self.ws_host}:{self.ws_port}"
                print(f"🔗 Connecting to {uri}...")

                async with websockets.connect(uri,
                                             ping_interval=20,
                                             ping_timeout=10) as websocket:
                    print("✅ WebSocket connected!")
                    self.websocket_connected = True
                    retry_count = 0

                    # Send initial connection messages for both paddles
                    for paddle_id in ["ai1", "ai2"]:
                        init_msg = {
                            "type": "ai_controller_connected",
                            "paddle": paddle_id,
                            "timestamp": time.time() * 1000
                        }
                        await websocket.send(json.dumps(init_msg))
                        paddle_name = self.paddle_states[paddle_id]["name"]
                        print(f"📤 Sent connection message for {paddle_name}: {init_msg}")

                    # Listen for messages
                    async for message in websocket:
                        try:
                            self.messages_received += 1

                            # Try to parse JSON
                            try:
                                data = json.loads(message)
                                print(f"\n📨 Message #{self.messages_received}: {data}")
                            except json.JSONDecodeError:
                                print(f"📨 Non-JSON message #{self.messages_received}: {message[:100]}...")
                                continue

                            # Look for ball state data
                            ball_data = None
                            if data.get('type') == 'ball_checkpoint':
                                ball_data = data.get('payload', {})
                                print(f"🏐 Ball checkpoint received: {ball_data}")
                            elif 'gameState' in data:
                                ball_data = data.get('gameState', {}).get('ball', {})
                                print(f"🏐 Game state ball: {ball_data}")
                            elif data.get('type') == 'ballcheckpoint':  # Alternative naming
                                ball_data = data.get('payload', {}) or data
                                print(f"🏐 Ball state: {ball_data}")

                            # If we have ball data, move BOTH paddles
                            if ball_data and isinstance(ball_data, dict):
                                has_position = (ball_data.get('position_x') is not None or
                                              ball_data.get('x') is not None)
                                if has_position:
                                    self.last_ball_data = ball_data

                                    print(f"\n🎮 MOVING BOTH PADDLES")
                                    print("=" * 40)

                                    # Move BOTH paddles simultaneously
                                    for paddle_id in ["ai1", "ai2"]:
                                        paddle_name = self.paddle_states[paddle_id]["name"]
                                        target_y = self.calculate_target_position(ball_data, paddle_id)

                                        print(f"\n🎮 {paddle_name} -> {target_y:.0f}")

                                        # CRITICAL: Send paddle movement using BOTH methods
                                        # Method 1: HTTP API (most reliable)
                                        http_success = self.send_paddle_command_http(paddle_id, target_y)

                                        # Method 2: WebSocket (for real-time updates)
                                        ws_success = await self.send_paddle_command_websocket(websocket, paddle_id, target_y)

                                        if http_success or ws_success:
                                            print(f"✅ {paddle_name} movement successful!")
                                        else:
                                            print(f"❌ {paddle_name} movement failed!")
                                else:
                                    print("⚠️ Ball data missing position information")

                            # Send acknowledgment
                            ack = {
                                "type": "message_received",
                                "paddles": ["ai1", "ai2"],
                                "timestamp": time.time() * 1000
                            }
                            await websocket.send(json.dumps(ack))

                        except Exception as e:
                            print(f"⚠️ Message processing error: {e}")
                            continue

            except websockets.exceptions.ConnectionClosed:
                retry_count += 1
                print(f"🔌 WebSocket closed. Retry {retry_count}/{max_retries}")
                if retry_count < max_retries:
                    await asyncio.sleep(2)
            except Exception as e:
                retry_count += 1
                print(f"❌ WebSocket error: {e}")
                if retry_count < max_retries:
                    await asyncio.sleep(2)

        print(f"💥 WebSocket connection failed after {max_retries} attempts")
        self.websocket_connected = False

    async def http_polling_fallback(self):
        """Fallback: poll HTTP API for ball data and move both paddles"""
        print("\n🔄 STARTING HTTP POLLING FALLBACK FOR BOTH PADDLES")
        print("=" * 60)

        while True:
            try:
                # Get ball data from HTTP API
                url = f"http://{self.http_host}:{self.http_port}/api/ball"
                response = requests.get(url, timeout=0.5)

                if response.status_code == 200:
                    ball_data = response.json()
                    if ball_data and isinstance(ball_data, dict):
                        # Move BOTH paddles based on ball position
                        for paddle_id in ["ai1", "ai2"]:
                            target_y = self.calculate_target_position(ball_data, paddle_id)
                            success = self.send_paddle_command_http(paddle_id, target_y)
                            if success:
                                paddle_name = self.paddle_states[paddle_id]["name"]
                                print(f"🔄 HTTP Poll: {paddle_name} moved to {target_y:.0f}")

                # Poll every 100ms
                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"⚠️ HTTP polling error: {e}")
                await asyncio.sleep(0.5)

    def print_status(self):
        """Print current debug status for both paddles"""
        print("\n📊 DUAL PADDLE DEBUG STATUS")
        print("=" * 40)
        print(f"WebSocket Connected: {self.websocket_connected}")
        print(f"Messages Received: {self.messages_received}")

        # Status for both paddles
        for paddle_id in ["ai1", "ai2"]:
            paddle_info = self.paddle_states[paddle_id]
            print(f"{paddle_info['name']}:")
            print(f"  Commands Sent: {paddle_info['commands_sent']}")
            print(f"  Current Y: {paddle_info['current_y']:.1f}")

        if self.last_ball_data:
            ball_x = self.last_ball_data.get('position_x', self.last_ball_data.get('x', 'N/A'))
            ball_y = self.last_ball_data.get('position_y', self.last_ball_data.get('y', 'N/A'))
            print(f"Last Ball Position: ({ball_x}, {ball_y})")

    async def run_debug_session(self):
        """Run the complete debug session for both paddles"""
        print("🔧 DUAL PADDLE PONG AI DEBUG CONTROLLER STARTED")
        print("=" * 70)
        print()
        print("🎯 Purpose: Fix paddle movement for BOTH AI paddles in Remote AI mode")
        print("🔍 This will test all communication methods and show detailed logs")
        print("🎮 Controls: LEFT paddle (ai1) AND RIGHT paddle (ai2)")
        print()

        # Step 1: Test HTTP endpoints
        self.test_http_endpoints()

        # Step 2: Start status monitoring
        status_task = None
        async def print_periodic_status():
            while True:
                await asyncio.sleep(10)
                self.print_status()

        status_task = asyncio.create_task(print_periodic_status())

        # Step 3: Try WebSocket connection first
        try:
            websocket_task = asyncio.create_task(self.websocket_main_loop())
            http_task = asyncio.create_task(self.http_polling_fallback())

            # Run both concurrently
            await asyncio.gather(websocket_task, http_task)
        except KeyboardInterrupt:
            print("\n🛑 Debug session stopped by user")
        finally:
            if status_task:
                status_task.cancel()

async def main():
    """Main debug function"""
    print("🔧 DUAL PADDLE PONG DEBUG CONTROLLER")
    print("=" * 60)
    print()
    print("⚠️ PROBLEM: Paddles not moving in Remote AI mode")
    print("🎯 SOLUTION: Debug all communication paths for BOTH paddles")
    print()
    print("🎮 This version controls BOTH ai1 (LEFT) and ai2 (RIGHT) paddles")
    print()
    print("📋 INSTRUCTIONS:")
    print("1. Make sure server.py is running")
    print("2. Open main.html in browser")
    print("3. Set game to 'Remote AI' mode")
    print("4. Press ENTER in game to start")
    print("5. Watch debug output to see both paddles moving")
    print()

    # Create dual paddle debug controller
    controller = DualPaddleDebugController()

    # Run debug session
    await controller.run_debug_session()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Dual paddle debug controller stopped")
