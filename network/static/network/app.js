document.addEventListener('DOMContentLoaded', function() {
    // Use buttons to toggle between views
    document.querySelector('#all-posts').addEventListener('click', () => loadPosts());
    document.querySelector('#create-post').addEventListener('click', () => toggleCreatePostView());
    document.querySelector('#create-post-form').addEventListener('submit', createPost);
    // By default, load all posts
    loadPosts();
});

/**
 * Load all posts and display them in the postsContainer.
 */
function loadPosts() {

    // Set the display properties of the containers
    const postsContainer = document.querySelector('#posts-view')
    postsContainer.style.display = 'block';
    document.querySelector('#create-post-view').style.display = 'none';
    document.querySelector('#user-profile-view').style.display = 'none';

    // Clear the contents of the postsContainer
    postsContainer.innerHTML = '';

    // Fetch the posts from the server
    fetch('/get_all_posts')
    .then(response => response.json())
    .then(posts => {
        // Iterate over each post
        posts.forEach(post => {
            // Create a div element for each post
            const postDiv = document.createElement('div');
            postDiv.className = 'post';

            // Set the innerHTML of the postDiv to display the post's title and content
            postDiv.innerHTML = `
            <div>
                Title: ${post.title}
            </div>
            <div>
                Content: ${post.content}
            </div>
            <div>
                Author: <a class="post_user" href="#" onclick="loadUserProfile('${post.username}')">${post.username}</a>
            </div>
            `;

            // Append post and like button to the postsContainer
            postsContainer.appendChild(postDiv);
        });
    })
    .catch(error => console.log(error)); // Add error handling
}

/**
 * Toggles the display of the create post view and posts view.
 * Hides the posts view and displays the create post view.
 */
function toggleCreatePostView() {
    // Hide the other views and display the create post view
    document.querySelector('#posts-view').style.display = 'none';
    document.querySelector('#user-profile-view').style.display = 'none';
    document.querySelector('#create-post-view').style.display = 'block';
}

/**
 * Function to create a post.
 * It prevents the default form submission behavior and fetches the data from the form.
 * It then sends a POST request to the '/create_post' endpoint with the post data.
 * After a successful response, it calls the loadPosts function to update the posts view.
 * It also clears the input fields.
 *
 * @param {Event} event - The event object representing the form submission event.
 */
function createPost(event) {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Get the input fields for title and content
    const titleInput = document.querySelector('#title');
    const contentInput = document.querySelector('#content');

    // Create an object with the post data
    const postData = {
        title: titleInput.value,
        content: contentInput.value
    };

    // Send a POST request to the '/create_post' endpoint with the post data
    fetch('/create_post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(postData)
    })
    // After a successful response, load the posts again
    .then(() => loadPosts());

    // Clear the input fields
    titleInput.value = '';
    contentInput.value = '';
}

function loadUserProfile (username) {

    document.querySelector('#user-profile-view').innerHTML = '';
    fetch(`/users/${username}`)
    .then(response => response.json())
    .then(user => {
        fetch(`/users/${username}/posts`)
        const userProfileContainer = document.querySelector('#user-profile-view');
        const profileDiv = document.createElement('div');
        profileDiv.innerHTML = `
        <div>
            Username: ${user.username}
        </div>
        <div>
            Followers: ${user.followers_count}
            Following: ${user.following_count}
        </div>
        <div>
            Posts: ${user.posts}
        </div>
        `;
        userProfileContainer.appendChild(profileDiv);
    })
    .catch(error => console.log(error))

    document.querySelector('#posts-view').style.display = 'none';
    document.querySelector('#create-post-view').style.display = 'none';
    document.querySelector('#user-profile-view').style.display = 'block';
}
