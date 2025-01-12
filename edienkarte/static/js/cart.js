function deleteItem(id) {
    fetch('/cart', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(id)
    })
    .then(response => response.json())
    .then(data => {
    console.log('Data submitted successfully:', data);
    window.location.href = '/cart';
    })
    .catch(error => {
    console.error('Error submitting data:', error);
    });
}