function user_search(){
  var user = document.getElementById('user_name').value;
  var password = document.getElementById('password').value;
  $.ajax({
    url:'/check_user',
    type: 'GET',
    data: {
      user: user,
      password: password
    },
    dataType: 'json',
    success: function(response){
      entries = Object.entries(response);
      console.log(entries[0][1]);
      if(entries[0][1] == false){
        document.getElementById('error_msg').value = 'Sorry, your username or password was invalid';
        return;
      }
      window.location.href = '/home';
    },
    error: function(response){
      console.log('error');
      document.getElementById('error_msg').value = 'Sorry, something went wrong in processing your request'
    }
  });
}
function set_user_for_home(){
  user = 'guest';
  password = '';
  $.ajax({
    url:'/check_user',
    type: 'GET',
    data: {
      user: user,
      password: password
    },
    dataType: 'json',
    success: function(response){
      entries = Object.entries(response);
      console.log(entries[0][1]);
      if(entries[0][1] == false){
        document.getElementById('error_msg').value = 'Sorry, your username or password was invalid';
      }
      window.location.href = '/home';
    },
    error: function(response){
      console.log('error');
      document.getElementById('error_msg').value = 'Sorry, something went wrong in processing your request'
    }
  });
}
