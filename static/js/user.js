const editForm = document.querySelector('#edit-form');
const editButton = document.querySelector('#edit-button');

editButton.addEventListener('click', (e) => {
	e.preventDefault();
	editForm.toggleAttribute('hidden')
});