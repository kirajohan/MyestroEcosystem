# Implementation Plan

[Overview]
Fix critical navigation and functionality issues in the Telegram bot by consolidating to a single keyboard system (ColoredKeyboard), adding missing handlers, and implementing comprehensive test coverage.

This plan addresses 5 critical bugs: duplicate keyboard systems causing conflicts, duplicate admin message handlers, missing back button navigation, incomplete settings menu, and missing test button. The solution consolidates all keyboard management to the modern ColoredKeyboard system and adds proper navigation handlers with context-aware routing.

[Types]
Single sentence describing the type system changes.

No new types required. Existing types from `bot/states/registration.py` will be utilized:
- `StartSection` - for non-registered user navigation
- `RegisteredSection` - for registered user navigation  
- `MenuSection` - for sub-menu state tracking
- `TestStates` - for test flow states

[Files]
Single sentence describing file modifications.

Detailed breakdown:
- **Modify**: `telegram_bot/bot/keyboards/reply.py` - Remove deprecated keyboard functions (main_menu_keyboard, registered_menu_keyboard) and update imports across codebase
- **Modify**: `telegram_bot/bot/handlers/menu.py` - Remove duplicate admin handler, add back_to_menu handler with context-aware navigation, fix settings back button
- **Modify**: `telegram_bot/bot/keyboards/orange_keyboard.py` - Add test button to reply_main_menu layout
- **Modify**: `telegram_bot/bot/handlers/contact.py` - Update to use ColoredKeyboard instead of old reply keyboards
- **Modify**: `telegram_bot/bot/handlers/register.py` - Update to use ColoredKeyboard consistently
- **Modify**: `telegram_bot/bot/handlers/profile.py` - Update imports to use ColoredKeyboard
- **Create**: `telegram_bot/tests/test_menu_navigation.py` - Test suite for menu navigation and back buttons
- **Create**: `telegram_bot/tests/test_admin_messages.py` - Test suite for admin message flow
- **Create**: `telegram_bot/tests/test_settings.py` - Test suite for settings menu

[Functions]
Single sentence describing function modifications.

Detailed breakdown:
- **Remove**: `main_menu_keyboard()` from `bot/keyboards/reply.py` - Replaced by ColoredKeyboard.reply_main_menu()
- **Remove**: `registered_menu_keyboard()` from `bot/keyboards/reply.py` - Replaced by ColoredKeyboard.reply_main_menu()
- **Modify**: `cmd_admin_message()` in `bot/handlers/menu.py` (lines 183-196) - Remove duplicate, keep this one for non-registered users
- **Remove**: `msg_admin()` in `bot/handlers/menu.py` (lines 224-236) - Duplicate handler, remove entirely
- **Add**: `back_to_menu()` in `bot/handlers/menu.py` - New handler for back_to_menu callback with context-aware routing based on user registration status
- **Modify**: `settings_kb()` in `bot/keyboards/inline.py` - Change back button callback from "back_to_menu" to "back_to_settings" for proper context navigation
- **Modify**: `reply_main_menu()` in `bot/keyboards/orange_keyboard.py` - Add "✅ Test" button to the layout (2-2-1 becomes 2-2-1 with test)
- **Update**: All `message.answer()` calls in contact.py, register.py, profile.py - Replace old keyboard imports with ColoredKeyboard

[Classes]
Single sentence describing class modifications.

No new classes required. Existing classes will be updated:
- `ColoredKeyboard` in `bot/keyboards/orange_keyboard.py` - Add test button to reply_main_menu() method
- `InboxState` in `bot/handlers/inbox.py` - No changes, already correct

[Dependencies]
Single sentence describing dependency modifications.

No new dependencies required. All changes use existing dependencies:
- `aiogram` - Already installed, used for all bot functionality
- `pytest` - Already in requirements, will be used for new test files
- `pytest-asyncio` - Already in requirements, needed for async test execution

[Testing]
Single sentence describing testing approach.

Create comprehensive test suite with 3 test files covering menu navigation, admin messages, and settings functionality using pytest and pytest-asyncio with mocked Telegram updates and FSM contexts.

Test requirements:
- `test_menu_navigation.py` - Test back button routing for registered/non-registered users, test main menu display
- `test_admin_messages.py` - Test admin message flow, message saving to backend, session state management
- `test_settings.py` - Test settings menu navigation, language change, AI toggle, logout flow
- All tests should mock `httpx.AsyncClient` to avoid real API calls
- All tests should use `aiogram.test` utilities for message/callback mocking

[Implementation Order]
Single sentence describing the implementation sequence.

Numbered steps showing the logical order of changes to minimize conflicts and ensure successful integration.

1. **Update ColoredKeyboard** - Add test button to reply_main_menu() in orange_keyboard.py
2. **Create back_to_menu handler** - Add context-aware navigation handler to menu.py
3. **Remove duplicate admin handler** - Delete msg_admin() function from menu.py (lines 224-236)
4. **Fix settings navigation** - Update settings_kb() back button callback to "back_to_settings"
5. **Update imports in contact.py** - Replace old keyboard imports with ColoredKeyboard
6. **Update imports in register.py** - Replace old keyboard imports with ColoredKeyboard  
7. **Update imports in profile.py** - Ensure consistent ColoredKeyboard usage
8. **Deprecate old reply.py keyboards** - Comment out or remove main_menu_keyboard() and registered_menu_keyboard()
9. **Create test suite** - Implement 3 test files with comprehensive coverage
10. **Run tests** - Execute pytest to verify all functionality works correctly