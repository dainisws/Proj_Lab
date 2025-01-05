function register() {
  const username = document.getElementById('registerUsername').value;
  const password = document.getElementById('registerPassword').value;

  if (username && password) {
      localStorage.setItem('username', username);
      localStorage.setItem('password', password);
      alert('Registration successful');
  } else {
      alert('Please fill in all fields');
  }
}

function login() {
  const loginUsername = document.getElementById('loginUsername').value;
  const loginPassword = document.getElementById('loginPassword').value;

  const storedUsername = localStorage.getItem('username');
  const storedPassword = localStorage.getItem('password');

  if (loginUsername === storedUsername && loginPassword === storedPassword) {
      alert('Login successful');
  } else {
      alert('Invalid username or password');
  }
}
