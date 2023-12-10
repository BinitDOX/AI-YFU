# AI-YFU
Artificial Intelligence-Yearning Fulfillment Unit, is a personalized AI telegram-based chatbot. It offers both text and voice chat capabilities, allowing you to interact with it naturally through your preferred method. It can even send you relevant images and proactively initiate conversations, adding a human touch to your digital interactions. This highly customizable AI assistant can learn your preferences and adapt to your specific needs, making it a true companion in the digital world.

## Notes:
### Pros:
- Minimal code, easyily customizable.
- Server (self) hosted on kaggle, bot (self) hosted on python-anywhere.
- Can initiate conversations seemlessly.
- Can send images, handle voice inputs and outputs.
- Has Long term memory.
- Does not immediately reply if in idle state.

### Cons:
- Project was made in two days (Sat-Sun), so code is very (bad) unstructured.
- Kaggle only provides ~30hr GPU weekly per account, so limited hosting.

### Other:
- Since gradio share is banned on kaggle (due to stable diffusion UIs) so we will use ngrok to bypass it.
- This project will most likely not be updated but you can easily make this into a full personal AI assitant. For example:
  1. Give full control over your phone using android accessibility API.
  2. Make calls, send text. Refer: https://github.com/shivaya-dav/DogeRat
  3. To collect your keystrokes randomly to make it more context aware about you.
  4. Ability to send stickers.
  5. Custom voice using SO-VITS.
  6. Able to sing songs using RVC
  7. Reply to past messages by sending a message-id along with each message.
  8. .... etc.


## Server Setup Instructions:
0. Download or clone the repository.
1. Make a <a href="https://www.kaggle.com/">kaggle</a> account and verify using phone to get ~30hrs of weekly GPU.
2. Make an <a href="https://ngrok.com/">ngrok</a> account and get your auth token from <a href="https://dashboard.ngrok.com/get-started/your-authtoken">here</a>
3. Go to <a href="https://www.kaggle.com/code/yeeandres/aiw-server">this</a> notebook and click 'Copy & Edit'
4. Set the accelerator as GPU P100 under notebook options if not already selected.
5. Replace the auth_token in '!ngrok config add-authtoken auth_token' in the notebook code with the auth-token in Step 3.
6. Edit the lore.txt and conversation.jsonl file. Replace the <...> with your custom text. Optinally, also change the date and time in the convo.
7. In the notebook, click on Upload data (beside the Add Data button). Browse and add both the lore and conversation file.
8. Enter dataset title as ai-data and click Create.
9. In the code, modify the user name, ai name and timezone under 'AI Settings'.
10. Click Run All and wait for ~15m. If eveything seems to be running correctly, click Save Version -> Save and Run All -> Save.
11. This will keep the server running in the backgroud on the kaggle machine (hosted) but takes ~15m to initialize.

## Bot Setup Instructions:
0. Download or clone the repository.
1. Create and setup a telegram bot using <a href="https://core.telegram.org/bots/features#botfather">these</a> instructions, and get the bot token. (Should take 5min)
2. Get your user id using <a href="https://cobrasystems.nl/en/telegram-user-id/">these</a> instructions.
3. Edit the AIW-client.py file and modify the config settings, add correct timezone, bot token, user id, ngrok token and the ai name used while setting up the server.
  - The TIMES_SELF_START property defines how many times in the range of FROM_HRS to TO_HRS will the AI, strike a conversation with you automatically.
  - The DELAYED_RESPONSES property defines that the AI can go into idle state (to make it human-like) and the first reply may take a few seconds to reply. This also allows you to send and enqueue multiple messages.
4. Make a <a href="https://www.pythonanywhere.com/">python-anywhere</a> account.
5. Goto Dashboard -> Files -> Upload a file and upload the AIW-Client.py file.
6. Goto Console and run:
  - pip install python-telegram-bot==13.3
  - pip install gradio-client
  - pip install ngrok-api
7. Finally run: (If you see a module not found error, install that module as well using pip install module-name)
  - python AIW-Client.py
8. The bot is also now hosted and will keep running (until Ctrl-C), it will also automatically connect the the server.
9. Start your bot by sending the /start command to your AI-YFU in telegram and enjoy!


## Credits:
- https://www.youtube.com/watch?v=OvY4o9zAqrU
- https://github.com/1neReality/M.I.T.S.U.H.A.
