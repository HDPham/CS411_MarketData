$(document).ready(function() {
  $('#login_form').submit(function(e) {
    e.preventDefault();
    $.ajax({
      url:'/check_user',
      type: 'POST',
      data: {
        username:$('#username').val(),
        password:$('#password').val()
      },
      dataType:'json',
      success: function(response) {
        console.log(response)
        if(response['info'] == true) { // if the login info is correct
          $.ajax({
            url:'/user_session',
            type: 'GET',
            data: {
              username:$('#username').val()
            },
            success: function(response) {
              window.location.href = '/home';
            },
            error: function(response) {
              document.getElementById('error_msg').value = 'Sorry, something went wrong in processing your request';
            }
          });
        }
        else // if the login info is incorret
          document.getElementById('error_msg').value = 'Sorry, your username or password was invalid';
      },
      error: function(response) {
        document.getElementById('error_msg').value = 'Sorry, something went wrong in processing your request'
      }
    });
  });

  $('#guest_btn').click(function() {
    $.ajax({
      url:'/user_session',
      type:'GET',
      data: {
        username:'Guest'
      },
      success: function(response) {
        console.log(response)
        window.location.href = '/home';
      },
      error: function(response) {
        console.log(response)
        document.getElementById('error_msg').value = 'Sorry, something went wrong in processing your request';
      }
    });
  });

});