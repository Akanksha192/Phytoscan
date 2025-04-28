window.onload = function() {
  const isLoggedIn = localStorage.getItem('loggedIn');
  const loginLogoutBtn = document.getElementById('login-logout-btn');
  
  if (isLoggedIn) {
    loginLogoutBtn.innerHTML = `<a class="btn btn-danger" href="#" onclick="logout()">Logout</a>`;
  } else {
    loginLogoutBtn.innerHTML = `<a class="btn btn-success" href="#" onclick="showLoginPage()">Login</a>`;
  }
};

function showLoginPage() {
  window.location.href = "/login";
}

function logout() {
  localStorage.removeItem('loggedIn');
  localStorage.removeItem('userEmail');
  alert("You have been logged out.");
  window.location.reload();
}
<script>
function toggleChat() {
    const chat = document.getElementById("chat-window");
    chat.style.display = chat.style.display === "flex" ? "none" : "flex";
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value;
    if (!message.trim()) return;

    const chatBox = document.getElementById("chat-messages");
    chatBox.innerHTML += `<div><strong>You:</strong> ${message}</div>`;
    input.value = "";

    const res = await fetch("/api/chat", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message })
    });

    const data = await res.json();
    if (data.reply) {
        chatBox.innerHTML += `<div><strong>G-Root Bot:</strong> ${data.reply}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    } else {
        chatBox.innerHTML += `<div><strong>Bot:</strong> Sorry, something went wrong.</div>`;
    }
}
</script>
