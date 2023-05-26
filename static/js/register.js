form = document.querySelector('form');
console.log(form);
username = document.querySelector('#username').value
email = document.querySelector('#email').value
password = document.querySelector('#password').value
confirmation = document.querySelector('#confirmation').value
message = document.querySelector('#message')
form.addEventListener('submit', (e) => {
	e.preventDefault()
	/*if (username == '' || email == '' || password == '' || confirmation == '') {
		message.innerHTML = '<strong>You must fill in all the inputs</strong>'
	}*/
	if (password != confirmation) {
		message.innerHTML = '<strong>Passwords don\'t match</strong>'
	} else {
		$.ajax({
			type: 'POST',
			url: '/register',
			data: {'username': username, 'email': email, 'password': password}
		})
	}
});