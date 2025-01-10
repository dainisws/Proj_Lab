function register() {
  const username = document.getElementById('registerUsername').value;
  const email = document.getElementById('registerEmail').value;
  const password = document.getElementById('registerPassword').value;
  const checkbox1 = document.getElementById('checkBox1');
  const checkbox2 = document.getElementById('checkBox2');

  if (!username || !email || !password) {
    alert('Please fill in all fields');
    return;
  }

  
  if (!checkbox1.checked || !checkbox2.checked) {
    alert('You must agree to the terms of service and privacy policy');
    return;
  }

  // Send user data to the Flask server
  fetch('/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email, password}),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Registration successful');
      window.location.href = '/signup';
    } else {
      alert(data.message || 'An error occurred');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('An error occurred while registering');
  });
}



function login() {
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  if (!email || !password) {
    alert('Please fill in all fields');
    return;
  }

  // Send login data to the Flask server
  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Redirect to home on successful login
      window.location.href = '/';
    } else {
      alert(data.message || 'Invalid credentials');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('An error occurred while logging in');
  });
}