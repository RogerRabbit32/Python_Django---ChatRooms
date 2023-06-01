document.addEventListener('DOMContentLoaded', function() {

    // We need to get the CSRF token from cookies
    function getCSRFToken() {
      const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        .split('=')[1];

      return cookieValue;
    }
    const csrfToken = getCSRFToken();
    console.log(csrfToken)

    // Add event listeners to all request participation buttons
    var requestButtons = document.querySelectorAll('.request-participation-btn');
    requestButtons.forEach(function(button) {
      button.addEventListener('click', function() {
        var chatId = this.getAttribute('data-chat-id');
        sendRequest(chatId);
      });
    });

    // Function to send the participation request
    function sendRequest(chatId) {
      var requestData = {
        chat: chatId,
        sender: '{{ request.user.id }}', // Current logged in user, who is requesting to join
      };

      fetch('/api/chat_rooms/requests/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(requestData)
      })
      .then(function(response) {
        if (response.ok) {
           // Request successful, change button text
          var button = document.querySelector('.request-participation-btn[data-chat-id="' + chatId + '"]');
          button.innerText = 'Request sent';
          button.disabled = true;
          console.log('Request sent successfully');
        } else {
          // Request failed, handle error
          console.log(response);
          console.error('Failed to send request');
        }
      })
      .catch(function(error) {
        console.error('Request error:', error);
      });
    }
  });