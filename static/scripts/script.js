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
  // Redirect to the login page
  window.location.href = "/login";
}

function logout() {
  // Clear the local storage and reset the logged-in state
  localStorage.removeItem('loggedIn');
  localStorage.removeItem('userEmail');
  alert("You have been logged out.");
  window.location.reload();
}
