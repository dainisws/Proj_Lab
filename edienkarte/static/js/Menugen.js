// Get the modal, open button, and close button
const modal = document.getElementById('modal');
const openModalBtn = document.getElementById('openModal');
const closeModalBtn = document.getElementById('closeModal');
let items = []; // All food groups
let items2 = []; // All foods
let modalLoaded = false;

// Open the modal
openModalBtn.addEventListener('click', () => {
  modal.style.display = 'flex';
  document.getElementById("searchInput1").value = "";
  document.getElementById("searchInput2").value = "";
  displayItems1(items.map(item => ({ name: item.name, id: item.id, rating: item.rating })));
  displayItems2(items2.map(item => ({ name: item.name, id: item.id, rating: item.rating })));

  if (modalLoaded) {
    return;
  }

  const button = document.getElementById("barbora");
  if (button.classList.contains("active")) {
    a = 0;
    fetch('/getbarboragroups')
    .then(response => response.json())
    .then(data => {
      items = data.map(item => ({ name: item.name, id: ++a, rating: "" }));
      displayItems1(items.map(item => ({ name: item.name, id: item.id, rating: item.rating})));
    }).catch(error => console.error("Error fetching items:", error));
    fetch('/getbarborafoods')
      .then(response => response.json())
      .then(data => {
        items2 = data.map(item => ({ id: item.id, name: item.name, rating: "" }));
        return fetch('/getbarboraratings')
      })
      .then(response => response.json())
      .then(data => {
        ratings = data.map(item => ({ id: item.id, rating: item.rating }));
        items2 = items2.map(item => {
          const matchingRating = ratings.find(rating => rating.id === item.id);
          if (matchingRating) {
            item.rating = matchingRating.rating;
          }
          return item;
        });
        displayItems2(items2.map(item => ({ name: item.name, id: item.id, rating: item.rating})));
        modalLoaded = true;
      }
    ).catch(error => console.error("Error fetching items:", error));
  } else {
    a = 0;
    fetch('/getrimigroups')
    .then(response => response.json())
    .then(data => {
      items = data.map(item => ({ name: item.name, id: ++a, rating: "" }));
      displayItems1(items.map(item => ({ name: item.name, id: item.id, rating: item.rating})));
    }).catch(error => console.error("Error fetching items:", error));
    fetch('/getrimifoods')
      .then(response => response.json())
      .then(data => {
        items2 = data.map(item => ({ id: item.id, name: item.name, rating: "" }));
        return fetch('/getrimiratings')
      })
      .then(response => response.json())
      .then(data => {
        ratings = data.map(item => ({ id: item.id, rating: item.rating }));
        items2 = items2.map(item => {
          const matchingRating = ratings.find(rating => rating.id === item.id);
          if (matchingRating) {
            item.rating = matchingRating.rating;
          }
          return item;
        });
        displayItems2(items2.map(item => ({ name: item.name, id: item.id, rating: item.rating})));
        modalLoaded = true;
      }
    ).catch(error => console.error("Error fetching items:", error));
  }
});

// Close the modal
closeModalBtn.addEventListener('click', () => {
  modal.style.display = 'none';
  document.getElementById("searchInput1").value = "";
  document.getElementById("searchInput2").value = "";
});

// Close the modal when clicking outside the content
window.addEventListener('click', (e) => {
  if (e.target === modal) {
    modal.style.display = 'none';
    document.getElementById("searchInput1").value = "";
    document.getElementById("searchInput2").value = "";
  }
});


function buttonClicked(button) {  
    modalLoaded = false;
    // Remove 'active' class from all buttons  
    document.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));  
    
    // Add 'active' class to the clicked button  
    button.classList.add('active');  
    
}  

function compute() {
  const minCalories = document.getElementById("minCalories").value;
  const maxCalories = document.getElementById("maxCalories").value;
  const minFat = document.getElementById("minFat").value;
  const maxFat = document.getElementById("maxFat").value;
  const minProtein = document.getElementById("minProtein").value;
  const maxProtein = document.getElementById("maxProtein").value;
  const minCarbs = document.getElementById("minCarbs").value;
  const maxCarbs = document.getElementById("maxCarbs").value;
  const weightTaste = document.getElementById("weights").value / 100.0;
  const weightPrice = 1 - weightTaste;
  let store = "Rimi"
  if (document.getElementById("barbora").classList.contains("active")) {
    store = "Barbora"
  }
  
  const foodGroupsWithRatings = items.filter(item => item.rating !== "");
  const foodsWithRatings = items2.filter(item => item.rating !== "");
  const computeType = "init";
  
  const dataToSend = {
    minCalories,
    maxCalories,
    minFat,
    maxFat,
    minProtein,
    maxProtein,
    minCarbs,
    maxCarbs,
    weightTaste,
    weightPrice,
    store,
    foodGroupsWithRatings,
    foodsWithRatings,
    computeType
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





























function updateFoodGroupRating(id, input) {
  let value = parseFloat(input.value);
  if ((value != "" && isNaN(value)) || value < 0 || value > 10) {
    input.value = "";
  }
  items = items.map(item => {
    if (item.id === id) {
      item.rating = value;
    }
    return item;
  });
}

function updateFoodRating(id, input) {
  let value = parseFloat(input.value);
  if ((value != "" && isNaN(value)) || value < 0 || value > 10) {
    input.value = "";
  }
  items2 = items2.map(item => {
    if (item.id === id) {
      item.rating = value;
    }
    return item;
  });
}






const resultsList1 = document.getElementById("food-section-1");

function displayItems1(filteredItems) {
  resultsList1.innerHTML = "";

  if (filteredItems.length === 0) {
    resultsList1.innerHTML = `<div class="food-item"><label>No Results</label></div>`;
    return;
  }

  filteredItems.forEach((item) => {
    resultsList1.innerHTML += `<div class="food-item"><label>${item.name}</label><input type="number" oninput="updateFoodGroupRating(${item.id}, this)" min="1" max="10" pattern="^([0-9]|10)$" value="${item.rating}"></div><hr>`;
  });
}

function filterItems1() {
  const query = document.getElementById("searchInput1").value.toLowerCase();
  const filteredItems = items.filter(
    item => item.name.toLowerCase().includes(query.toLowerCase())).map(item => ({ name: item.name, id: item.id, rating: item.rating})
  );
  displayItems1(filteredItems);
}

const resultsList2 = document.getElementById("food-section-2");

function displayItems2(filteredItems) {
  resultsList2.innerHTML = "";

  if (filteredItems.length === 0) {
    resultsList2.innerHTML = `<div class="food-item"><label>No Results</label></div>`;
    return;
  }

  filteredItems.forEach((item) => {
    resultsList2.innerHTML += `<div class="food-item"><label>${item.name}</label><input type="number" oninput="updateFoodRating(${item.id}, this)" min="1" max="10" pattern="^([0-9]|10)$" value="${item.rating}"></div><hr>`;
  });
}

function filterItems2() {
  const query = document.getElementById("searchInput2").value.toLowerCase();
  const filteredItems = items2.filter(
    item => item.name.toLowerCase().includes(query.toLowerCase())).map(item => ({ name: item.name, id: item.id, rating: item.rating})
  );
  displayItems2(filteredItems);
}