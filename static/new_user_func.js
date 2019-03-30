function call_insert_user(){
  var user = document.getElementById('new_user').value;
  var password = document.getElementById('new_password').value;
  $.ajax({
    url:'/insert_user',
    type: 'POST',
    data:{
      user:user,
      password:password
    },
    success: function(response){
      console.log('success');
      window.location.href = '/home';
    },
    error: function(response){
      console.log('error');
    }
  });
}
