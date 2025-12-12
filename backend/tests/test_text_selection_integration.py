import asyncio
import websockets
import json
import time
from typing import Dict, Any


async def test_text_selection_workflow():
    """
    Test complete text selection workflow:
    1. WebSocket connection
    2. Text selection context
    3. Query with context
    4. Response validation
    """

    print("🚀 Starting Text Selection Integration Test...")

    # Test WebSocket connection
    uri = "ws://localhost:8000/ws/chat"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established")

            # Test 1: Basic connection and welcome message
            welcome_message = await websocket.recv()
            welcome_data = json.loads(welcome_message)
            assert welcome_data.get("type") == "welcome", (
                f"Expected welcome message, got: {welcome_data.get('type')}"
            )
            print("✅ Welcome message received")

            # Test 2: Query with text selection context
            query_with_context = {
                "type": "question",
                "data": {
                    "question": "What is Zero Moment Point in robotics?",
                    "context_chunks": [
                        "The Zero Moment Point (ZMP) is a crucial concept in bipedal robot dynamics. It represents the point on the ground where the total moment of all forces acting on the robot equals zero.",
                        "ZMP stability criterion states that for a robot to maintain dynamic balance, the ZMP must remain within the support polygon formed by the robot's feet.",
                    ],
                },
            }

            await websocket.send(json.dumps(query_with_context))
            print("✅ Query with context sent")

            # Test 3: Collect and validate response
            response_chunks = []
            response_start_received = False
            response_end_received = False

            start_time = time.time()

            while (
                not response_end_received and (time.time() - start_time) < 10
            ):  # 10 second timeout
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    message_type = data.get("type")

                    if message_type == "response_start":
                        response_start_received = True
                        print("✅ Response start received")

                    elif message_type == "response_chunk":
                        response_chunks.append(data.get("data", {}))

                    elif message_type == "response_end":
                        response_end_received = True
                        response_time = data.get("data", {}).get("response_time_ms", 0)
                        print(f"✅ Response end received (time: {response_time}ms)")

                        # Validate response time meets requirement (<2000ms)
                        assert response_time < 2000, (
                            f"Response time {response_time}ms exceeds 2000ms requirement"
                        )

                except asyncio.TimeoutError:
                    continue

            # Test 4: Validate response content
            assert response_start_received, "No response start message received"
            assert response_end_received, "No response end message received"
            assert len(response_chunks) > 0, "No response chunks received"

            # Combine all response chunks
            full_response = "".join(
                [chunk.get("content", "") for chunk in response_chunks]
            )

            print(f"✅ Full response received ({len(full_response)} characters)")

            # Test 5: Validate context awareness
            response_lower = full_response.lower()
            context_indicators = [
                "zero moment point",
                "zmp",
                "balance",
                "stability",
                "support polygon",
            ]

            context_found = any(
                indicator in response_lower for indicator in context_indicators
            )
            assert context_found, (
                f"Response does not show awareness of context: {response_lower[:200]}..."
            )
            print("✅ Response shows context awareness")

            # Test 6: Validate source citations (should include references)
            source_indicators = ["chapter", "section", "according to", "source"]
            sources_cited = any(
                indicator in response_lower for indicator in source_indicators
            )
            assert sources_cited, "Response does not include source citations"
            print("✅ Response includes source citations")

            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Text selection workflow is fully functional")
            print("✅ Context-aware responses working")
            print("✅ Performance requirements met")
            print("✅ Constitution compliance achieved")

            return True

    except websockets.exceptions.ConnectionRefusedError:
        print("❌ WebSocket connection refused - is the backend running?")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_multiple_context_chunks():
    """
    Test handling of multiple context chunks (up to 5 limit)
    """

    print("\n🔄 Testing Multiple Context Chunks...")

    uri = "ws://localhost:8000/ws/chat"

    try:
        async with websockets.connect(uri) as websocket:
            # Wait for welcome message
            await websocket.recv()

            # Test with 5 context chunks (maximum allowed)
            query_with_multiple_context = {
                "type": "question",
                "data": {
                    "question": "How do these concepts relate to robot stability?",
                    "context_chunks": [
                        "Center of mass (COM) is the average position of all mass in the robot.",
                        "Center of pressure (COP) is the point where ground reaction forces act.",
                        "The relationship between COM and COP determines stability.",
                        "For static balance, COM must be vertically above COP.",
                        "Dynamic balance requires anticipating COM movement.",
                    ],
                },
            }

            await websocket.send(json.dumps(query_with_multiple_context))

            # Collect response
            response_received = False
            start_time = time.time()

            while not response_received and (time.time() - start_time) < 5:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    if data.get("type") == "response_end":
                        response_received = True
                        print("✅ Multiple context chunks handled successfully")

                except asyncio.TimeoutError:
                    continue

            assert response_received, "No response received for multiple context chunks"
            return True

    except Exception as e:
        print(f"❌ Multiple context test failed: {e}")
        return False


async def test_context_chunk_limit():
    """
    Test that more than 5 context chunks are rejected
    """

    print("\n🚫 Testing Context Chunk Limit...")

    uri = "ws://localhost:8000/ws/chat"

    try:
        async with websockets.connect(uri) as websocket:
            # Wait for welcome message
            await websocket.recv()

            # Test with 6 context chunks (should be rejected)
            query_with_too_many_context = {
                "type": "question",
                "data": {
                    "question": "Test question",
                    "context_chunks": [
                        f"Context chunk {i}"
                        for i in range(6)  # 6 chunks - exceeds limit
                    ],
                },
            }

            await websocket.send(json.dumps(query_with_too_many_context))

            # Should receive an error message
            error_received = False
            start_time = time.time()

            while not error_received and (time.time() - start_time) < 5:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    if data.get("type") == "error":
                        error_received = True
                        error_message = data.get("data", {}).get("message", "")
                        assert (
                            "context" in error_message.lower()
                            or "chunk" in error_message.lower()
                        )
                        print("✅ Context chunk limit properly enforced")

                except asyncio.TimeoutError:
                    continue

            assert error_received, "Expected error for too many context chunks"
            return True

    except Exception as e:
        print(f"❌ Context limit test failed: {e}")
        return False


async def main():
    """Run all text selection integration tests"""

    print("=" * 60)
    print("TEXT SELECTION INTEGRATION TEST SUITE")
    print("Constitution Requirement Validation")
    print("=" * 60)

    tests = [
        ("Text Selection Workflow", test_text_selection_workflow),
        ("Multiple Context Chunks", test_multiple_context_chunks),
        ("Context Chunk Limit", test_context_chunk_limit),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)

        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Constitution requirements fully validated")
        print("✅ Text selection context system is production ready")
    else:
        print("❌ Some tests failed - check implementation")

    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
