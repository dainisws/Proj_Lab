// Get the modal, open button, and close button
const modal = document.getElementById('modal');
const openModalBtn = document.getElementById('openModal');
const closeModalBtn = document.getElementById('closeModal');

// Open the modal
openModalBtn.addEventListener('click', () => {
  modal.style.display = 'flex';
});

// Close the modal
closeModalBtn.addEventListener('click', () => {
  modal.style.display = 'none';
});

// Close the modal when clicking outside the content
window.addEventListener('click', (e) => {
  if (e.target === modal) {
    modal.style.display = 'none';
  }
});


function buttonClicked(button) {  
    // Remove 'active' class from all buttons  
    document.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));  
    
    // Add 'active' class to the clicked button  
    button.classList.add('active');  
    
}  