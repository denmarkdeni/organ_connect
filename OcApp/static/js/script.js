function toggleReviews() {
    let hiddenReviews = document.querySelectorAll('.hidden');
    let button = document.getElementById('toggleButton');

    if (button.innerText === "Show More") {
        hiddenReviews.forEach((review, index) => {
            setTimeout(() => {
                review.style.display = 'flex';
                setTimeout(() => {
                    review.style.opacity = '1';
                    review.style.transform = 'scale(1)';
                }, 50);
            }, index * 100);
        });
        button.innerText = "See Less";
    } else {
        hiddenReviews.forEach((review, index) => {
            setTimeout(() => {
                review.style.opacity = '0';
                review.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    review.style.display = 'none';
                }, 500);
            }, index * 100);
        });
        button.innerText = "Show More";
    }
}

document.getElementById('addReviewForm').addEventListener('submit', function(event) {
    event.preventDefault();
    console.log(isAuthenticated)
    if (isAuthenticated == 'False') {
        alert("Only logged-in users can review.");
        window.location.href = '/login-register/';
        return;
    }
    let name = document.getElementById('name').value;
    let gender = document.getElementById('gender').value;
    let reviewText = document.getElementById('reviewText').value;

    if (name && gender && reviewText) {
        fetch('/add_review/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                name: name,
                gender: gender,
                reviewText: reviewText,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                let reviewList = document.getElementById('testimonialContainer');
                let newReview = document.createElement('div');
                newReview.className = 'testimonial-card';
                newReview.innerHTML = `
                    <img src="/static/images/${gender === 'M' ? 'boy.png' : 'girl.png'}" alt="${name}">
                    <p>"${reviewText}"</p>
                    <h3>- ${name}</h3>
                `;
                reviewList.prepend(newReview);
                
                document.getElementById('name').value = '';
                document.getElementById('gender').value = '';
                document.getElementById('reviewText').value = '';
                
                alert('Thank you for your review!');
                
                // Update toggle button visibility
                let reviews = document.querySelectorAll('.testimonial-card');
                if (reviews.length > 3) {
                    let toggleButton = document.getElementById('toggleButton');
                    if (!toggleButton) {
                        toggleButton = document.createElement('button');
                        toggleButton.id = 'toggleButton';
                        toggleButton.innerText = 'Show More';
                        toggleButton.onclick = toggleReviews;
                        reviewList.parentNode.appendChild(toggleButton);
                    }
                    reviews.forEach((review, index) => {
                        if (index >= 3) {
                            review.classList.add('hidden');
                            review.style.display = 'none';
                            review.style.opacity = '0';
                            review.style.transform = 'scale(0.95)';
                        }
                    });
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    } else {
        alert('Please fill in all fields.');
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}