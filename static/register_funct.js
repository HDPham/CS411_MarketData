$(document).ready(function() {
  $('#register_form').submit(function(e) {
    e.preventDefault();
    $.ajax({
      url:'/insert_user',
      type:'POST',
      data: {
        username:$('#new_username').val(),
        password:$('#new_password').val()
      },
      dataType:'json',
      success: function(response) {
        if(response['duplicate'] == false) { // if there exists no duplicate user
          window.location.href = '/home';
        }
        else 
          document.getElementById('error_msg').value = 'Sorry, that username is taken';
      },
      error: function(response){
        document.getElementById('error_msg').value = 'Sorry, something went wrong in processing your request'
      }
    });
  });
});