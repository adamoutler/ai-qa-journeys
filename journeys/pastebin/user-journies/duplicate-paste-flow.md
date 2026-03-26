---
name: Duplicate and Edit Paste
description: Verify a user can duplicate an existing paste, edit it, and save the changes.
purpose: The purpose of this journey is to validate the duplication and hotkey functionality of the application. It ensures that duplicating a paste creates a new editable state and that keyboard shortcuts (Ctrl-D, Ctrl-S, Ctrl-Shift-R) behave as expected.
limitations: Do not use curl, form-filling, dom manipulation or user inaccessible methods to fill forms. You must validate elements are on-screen, interact via physical-style mouse and keyboard events, and observe visual changes.
python_dependencies:
  - "playwright"
  - "beautifulsoup4"
setup_commands:
  - "playwright install --with-deps chromium"
environmental_variables:
  BASE_URL: http://hackedyour.info
  RANDOM_TEXT: ${RANDOM_HASH_OF_SOMETHING}
assertions:
  - "QA PASSED"
  - "FINAL_URL: https?://hackedyour.info/[a-zA-Z0-9]+"
  - "${RANDOM_TEXT}abc"
---
# Verification of Duplicate and Edit:
Your task is to act as a user and verify the following sequence:

1. **Initial Creation**:
   - Navigate to $BASE_URL.
   - Enter "${RANDOM_TEXT}" into the main window where prompt text "Paste here" exists.
   - Press the save button (or Ctrl-S).
   - Verify the URL has changed, indicating a successful save.

2. **Duplication**:
   - Press **Ctrl-D** to trigger the "Duplicate" action.
   - Wait at least 1 second for the new editor instance to initialize.

3. **Editing**:
   - Type the characters **a**, then **b**, then **c** (using individual key events).
   - Press **Ctrl-S** to save the duplicated and modified paste.

4. **Raw Verification**:
   - Press **Ctrl-Shift-R** to open the "Raw" view of the current paste.
   - Verify that the resulting page contains exactly "${RANDOM_TEXT}abc".

At the end of your test execution, follow the reporting requirements in your system prompt.
