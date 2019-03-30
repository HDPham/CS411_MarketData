$(document).ready(function (){
  console.log('ready');
  call_get_user_info();
  $.ajax({
    url:'/get_user_stocks',
    type: 'GET',
    success: function(response){
      document.getElementById('user_tracked_stocks').value = response;
    },
    error: function(response){
      console.log('error');
      document.getElementById('user_info_output').value = "Bwahaha Thomas, you have thwarted yourself once again";
    }
  });
})

function call_get_user_info(){
  $.ajax({
    url:'/get_user_info',
    type:'GET',
    success: function(response){
      var result = JSON.parse(response);
      document.getElementById('user_info_output').value = response;
      console.log(result.user);
      document.getElementById('user_info_table').rows[0].cells[1].value = result.user;
      document.getElementById('user_info_table').rows[1].cells[1].value = result.password;
    },
    error: function(response){
      document.getElementById('user_info_output').value = "Bwahaha Thomas, you have thwarted yourself once again";
    }
  });
}
function call_update_user_info(){
  password = document.getElementById('new_password').value;
  confirm_password = document.getElementById('confirm_password').value;
  console.log(password); console.log(confirm_password);
  if(password != confirm_password){
    document.getElementById('user_info_output').value = 'Sorry, your passwords don\'t match :/ ';
  }
  $.ajax({
    url:'/update_user_info',
    type: 'POST',
    data: {
      password: password
    },
    success: function(response){
      console.log('success');
    },
    error: function(response){
      console.log('error, so sad :(');
    }
  });
  call_get_user_info();
}
