


document.getElementById('login-form').addEventListener('submit', function(event) {
  event.preventDefault();

  // Get the username and password values
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  // Simple validation for empty fields
  if (username === "" || password === "") {
    alert("Both fields are required.");
    return;
  }

  // Simulate successful login (can replace with actual API calls)
  alert("Login successful!");


});
