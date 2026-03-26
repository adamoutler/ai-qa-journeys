---
name: Create a paste
description: Verify a user can create a paste and share it.
purpose: The purpose of this journey is to act as a user. The goal is to use screenshot analysis, mouse clicks, input key events and scrolling rather than broad knowledge of the DOM  and automated form filling.
limitations: Do not use curl, form-filling, dom manipulation or user inaccessible methods to fill forms.  You must validate the element is on-screen, then send a click even to the location of that element and use input keyevents to populate it.
python_dependencies:
  - "playwright"
  - "beautifulsoup4"
setup_commands:
  - "playwright install --with-deps chromium"
environmental_variables:
  BASE_URL: http://hackedyour.info
  RANDOM_TEXT: ${RANDOM_HASH_OF_SOMETHING}
---
# Verification of Paste:
Your task is to act as a user and verify the following:

- "Navigate to $BASE_URL"
- "Enter \"${RANDOM_TEXT} into main window where prompt text \"Paste here\" exists."
- "Press the save button."
- "Copy the URL at the top of the page after save."
- "Open the URL in a new tab."
- "Verify the text \"${RANDOM_TEXT}\" appears on the page."