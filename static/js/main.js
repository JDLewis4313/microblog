function updateWelcome() {
    document.getElementById("welcome-message").innerHTML = "What IΓÇÖm Learning, Building, and Breaking (on Purpose)";
  }
function toggleChat() {
  const chatWindow = document.getElementById("chat-window");
  chatWindow.style.display = chatWindow.style.display === "none" ? "block" : "none";
}

function sendMessage() {
  const input = document.getElementById("chat-input");
  const log = document.getElementById("chat-log");
  const message = input.value.trim().toLowerCase();

  let response = "I'm still learning — try asking about Python or Flask!";
  if (message.includes("python")) {
    response = "Python is my favorite — clean and powerful.";
  } else if (message.includes("flask")) {
    response = "Flask gives you full control — perfect for modular apps.";
  } else if (message.includes("java")) {
    response = "Java taught me modularity and separation of concerns.";

  }

  log.innerHTML += `<p><strong>You:</strong> ${input.value}</p>`;
  log.innerHTML += `<p><strong>Bot:</strong> ${response}</p>`;
  input.value = "";
}
