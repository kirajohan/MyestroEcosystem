#!/usr/bin/env python3
"""Test script to verify the placeholder registry import fix.

This script verifies that:
1. The bot can import placeholder_registry without errors
2. The module has the expected structure
3. Fallback placeholders are available
"""

import sys
import asyncio
from pathlib import Path

# Add telegram_bot to path
telegram_bot_path = Path(__file__).parent
sys.path.insert(0, str(telegram_bot_path))


def test_import():
    """Test that placeholder_registry can be imported."""
    print("=" * 60)
    print("TEST 1: Import placeholder_registry module")
    print("=" * 60)
    
    try:
        from bot.services.placeholder_registry import (
            PLACEHOLDER_REGISTRY,
            get_placeholders,
            get_placeholders_from_backend,
            get_safe_user_fields,
        )
        print("[OK] Successfully imported placeholder_registry")
        print(f"   - PLACEHOLDER_REGISTRY: {type(PLACEHOLDER_REGISTRY)}")
        print(f"   - get_placeholders: {type(get_placeholders)}")
        print(f"   - get_placeholders_from_backend: {type(get_placeholders_from_backend)}")
        print(f"   - get_safe_user_fields: {type(get_safe_user_fields)}")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_fallback_placeholders():
    """Test that fallback placeholders are available."""
    print("\n" + "=" * 60)
    print("TEST 2: Check fallback placeholders")
    print("=" * 60)
    
    try:
        from bot.services.placeholder_registry import PLACEHOLDER_REGISTRY
        
        if not PLACEHOLDER_REGISTRY:
            print("[FAIL] PLACEHOLDER_REGISTRY is empty")
            return False
        
        print(f"[OK] PLACEHOLDER_REGISTRY contains {len(PLACEHOLDER_REGISTRY)} placeholders")
        
        # Check structure - should be a dict
        if not isinstance(PLACEHOLDER_REGISTRY, dict):
            print(f"[FAIL] PLACEHOLDER_REGISTRY should be dict, got {type(PLACEHOLDER_REGISTRY)}")
            return False
        
        # Check first key
        first_key = list(PLACEHOLDER_REGISTRY.keys())[0]
        print(f"   Sample key: {first_key}")
        print(f"   Keys available: {list(PLACEHOLDER_REGISTRY.keys())[:5]}...")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


async def test_async_functions():
    """Test async functions."""
    print("\n" + "=" * 60)
    print("TEST 3: Test async functions")
    print("=" * 60)
    
    try:
        from bot.services.placeholder_registry import (
            get_placeholders_from_backend,
            get_safe_user_fields,
        )
        
        # Test get_placeholders_from_backend (will use cache or fallback)
        print("Testing get_placeholders_from_backend()...")
        placeholders = await get_placeholders_from_backend()
        print(f"[OK] Got {len(placeholders)} placeholders")
        
        # Verify format - should be dict
        if not isinstance(placeholders, dict):
            print(f"[FAIL] Expected dict, got {type(placeholders)}")
            return False
        
        # Show sample
        first_key = list(placeholders.keys())[0]
        print(f"   Sample: {first_key} -> {placeholders[first_key]}")
        
        # Test get_safe_user_fields
        print("Testing get_safe_user_fields()...")
        safe_fields = await get_safe_user_fields()
        print(f"[OK] Got {len(safe_fields)} safe fields")
        print(f"   Sample fields: {safe_fields[:5]}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_broadcast_worker_import():
    """Test that broadcast_worker can import without errors."""
    print("\n" + "=" * 60)
    print("TEST 4: Test broadcast_worker import")
    print("=" * 60)
    
    try:
        # This will import broadcast_worker which imports placeholder_registry
        from bot.services.broadcast_worker import BroadcastWorker, render_template
        print("[OK] Successfully imported broadcast_worker")
        print(f"   - BroadcastWorker: {type(BroadcastWorker)}")
        print(f"   - render_template: {type(render_template)}")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PLACEHOLDER REGISTRY IMPORT FIX - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Import
    results.append(("Import test", test_import()))
    
    # Test 2: Fallback placeholders
    results.append(("Fallback placeholders", test_fallback_placeholders()))
    
    # Test 3: Async functions
    results.append(("Async functions", asyncio.run(test_async_functions())))
    
    # Test 4: Broadcast worker import
    results.append(("Broadcast worker import", test_broadcast_worker_import()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! The import fix is working correctly.")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())