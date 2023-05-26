const userPhoto = document.querySelector('#picture');
const userId = '{{ user.id }}';
const urlPhotos = '{{ url_for("static", filename="photos/") }}'
userPhoto.style.backgroundImage = `url(${urlPhotos}${userId}.jpg)`;
userPhoto.style.backgroundSize = 'cover';
userPhoto.style.backgroundPosition = 'center';