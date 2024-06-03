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
    // Select the postsContainer and createPostContainer elements
    const postsContainer = document.querySelector('#posts-view');
    const createPostContainer = document.querySelector('#create-post-view');

    // Set the display properties of the containers
    postsContainer.style.display = 'block';
    createPostContainer.style.display = 'none';

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
            postDiv.className = 'post ';

            // Create a like button element for each post
            const likeButton = document.createElement('button');
            likeButton.class = 'btn btn-primary';

            likeButton.addEventListener('click', () => likePost(post.id));

            if (post.likes > 0) {
                likeButton.innerHTML = 'Unlike';
            } else {
                likeButton.innerHTML = 'Like';
            } 
            
            // Set the innerHTML of the postDiv to display the post's title and content
            postDiv.innerHTML = `
            <div class="col-3 text-truncate">
                Title: ${post.title}
            </div>
            <div class="col-6 text-truncate">
                Content: ${post.content}
            </div>
            <div class="col-3 text-truncate">
                Author: ${post.author}
            </div>
            <div class="col-3 text-truncate">
                Likes: ${post.likes}
            </div> 
            `;

            // Append post and like button to the postsContainer
            postsContainer.appendChild(postDiv);
            postDiv.appendChild(likeButton);
        });
    });
}

/**
 * Toggles the display of the create post view and posts view.
 * Hides the posts view and displays the create post view.
 */
function toggleCreatePostView() {
    // Select the postsContainer and createPostContainer elements
    const postsContainer = document.querySelector('#posts-view');
    const createPostContainer = document.querySelector('#create-post-view');

    // Hide the posts view and display the create post view
    postsContainer.style.display = 'none';
    createPostContainer.style.display = 'block';
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

/**
 * Function to like a post.
 * It sends a POST request to the '/like_post/{postId}' endpoint.
 * After a successful response, it calls the loadPosts function to update the posts view.
 *
 * @param {number} postId - The id of the post to like.
 */
likePost = (postId) => {
    // Send a POST request to the '/like_post/{postId}' endpoint
    fetch(`/like_post/${postId}`)
    // After a successful response, load the posts again
    .then(() => loadPosts());
}
