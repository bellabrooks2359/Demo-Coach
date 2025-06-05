<!-- templates/coach_demo.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Sisuu Coaching Assistant</title>
  <style>
    body {
      font-family: sans-serif;
      background: #f5f5f5;
      padding: 2em;
    }
    .chat-box {
      background: white;
      max-width: 600px;
      margin: auto;
      padding: 1.5em;
      border-radius: 12px;
      box-shadow: 0 5px 12px rgba(0, 0, 0, 0.1);
    }
    .message { margin: 1em 0; }
    .user { font-weight: bold; }
    .sisuu { margin-top: 0.5em; color: #333; }
    input, button {
      padding: 0.75em;
      width: 100%;
      border-radius: 6px;
      margin-top: 1em;
      border: 1px solid #ccc;
    }
  </style>
</head>
<body>
  <div class="chat-box" id="chat">
    <div class="message">
      <div class="sisuu"><strong>Sisuu:</strong> Hi 👋 I'm here to help you think through situational challenges with your manager based on your working styles.</div>
    </div>
  </div>
  <input type="text" id="userInput" placeholder="Ask Sisuu a question..." />
  <button onclick="sendMessage()">Send</button>

  <script>
    async function sendMessage() {
      const input = document.getElementById("userInput");
      const chat = document.getElementById("chat");
      const question = input.value.trim();
      if (!question) return;

      chat.innerHTML += `<div class="message"><div class="user">You:</div><div>${question}</div></div>`;
      input.value = "";

      const res = await fetch("/coach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question })
      });

      const data = await res.json();
      const response = data.response || "Sorry, something went wrong.";

      chat.innerHTML += `<div class="message"><div class="sisuu"><strong>Sisuu:</strong> ${response}</div></div>`;
    }
  </script>
</body>
</html>
