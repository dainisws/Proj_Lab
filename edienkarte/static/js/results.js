document.getElementById("searchInput1").value = "";
document.getElementById("searchInput2").value = "";
const resultsList1 = document.getElementById("food-section-1");
const resultsList2 = document.getElementById("food-section-2");
displayItems1(items.map(item => ({ name: item[6], link: item[7], amount: item[8], id: item.id })));
displayItems2(items2.map(item => ({ name: item[6], link: item[7], amount: item[8], id: item.id })));


function updateAmount1(id, input) {
  let value = parseFloat(input.value);
  if ((value != "" && isNaN(value)) || value < 0 || value > 9999999) {
    input.value = "";
  }
  items = items.map(item => {
    if (item.id === id) {
      item[8] = value;
    }
    return item;
  });
}

function updateAmount2(id, input) {
    let value = parseFloat(input.value);
    if ((value != "" && isNaN(value)) || value < 0 || value > 9999999) {
      input.value = "";
    }
    items2 = items2.map(item => {
      if (item.id === id) {
        item[8] = value;
      }
      return item;
    });
  }





function submitData(item) {
    const computetype = "addToCart";
    const dataToSend = {
        item,
        computetype
    };

    fetch('/compute', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {
    console.log('Data submitted successfully:', data);
    window.location.href = '/compute';
    })
    .catch(error => {
    console.error('Error submitting data:', error);
    });
}

function addToCart1(id) {
    submitData(items.find(item => item.id === id));
}

function addToCart2(id) {
    submitData(items2.find(item => item.id === id));
}

function displayItems1(filteredItems) {
  resultsList1.innerHTML = "";

  if (filteredItems.length === 0) {
    resultsList1.innerHTML = `<div class="food-item"><label>No Results</label></div>`;
    return;
  }

  filteredItems.forEach((item) => {
    resultsList1.innerHTML += `<div class="food-item"><label><a href="${item.link}" target="_blank">${item.name}</a></label><div><input type="number" oninput="updateAmount1(${item.id}, this)" min="1" max="9999999" pattern="^([0-9]|10)$" value="${item.amount}"><button class="add-to-cart-btn" onclick="addToCart1(${item.id})">Add to Cart</button></div></div><hr>`;
  });
}

function filterItems1() {
  const query = document.getElementById("searchInput1").value.toLowerCase();
  const filteredItems = items.filter(
    item => item[6].toLowerCase().includes(query.toLowerCase())).map(item => ({ name: item[6], link: item[7], amount: item[8], id: item.id})
  );
  displayItems1(filteredItems);
}

function displayItems2(filteredItems) {
  resultsList2.innerHTML = "";

  if (filteredItems.length === 0) {
    resultsList2.innerHTML = `<div class="food-item"><label>No Results</label></div>`;
    return;
  }

  filteredItems.forEach((item) => {
    resultsList2.innerHTML += `<div class="food-item"><label><a href="${item.link}" target="_blank">${item.name}</a></label><div><input type="number" oninput="updateAmount2(${item.id}, this)" min="1" max="9999999" pattern="^([0-9]|10)$" value="${item.amount}"><button class="add-to-cart-btn" onclick="addToCart2(${item.id})">Add to Cart</button></div></div><hr>`;
  });
}

function filterItems2() {
  const query = document.getElementById("searchInput2").value.toLowerCase();
  const filteredItems = items2.filter(
    item => item[6].toLowerCase().includes(query.toLowerCase())).map(item => ({ name: item[6], link: item[7], amount: item[8], id: item.id })
  );
  displayItems2(filteredItems);
}