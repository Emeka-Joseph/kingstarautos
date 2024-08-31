def test_pagenotfound_route(client):
    # Create a test client
    with client:
        # Set up session data to simulate a logged-in user
        with client.session_transaction() as sess:
            sess['loggedin'] = 1  # Assuming user_id=1 for a test user

        # Send a GET request to a non-existent route
        response = client.get('/non-existent-route')

        # Check that the response status code is 404
        assert response.status_code == 404

        # Check that the response renders the error404.html template with the user data
        assert b'users/error404.html' in response.data
        assert b'alluser' in response.data