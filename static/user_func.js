$(document).ready(function (){
  console.log('ready');
  call_get_user_info();
  $.ajax({
    url:'/get_user_stocks',
    type: 'GET',
    success: function(response){
      make_user_stock_table(response);
    },
    error: function(response){
      console.log("Bwahaha Thomas, you have thwarted yourself once again");
    }
  });
})

function call_get_user_info(){
  $.ajax({
    url:'/get_user_info',
    type:'GET',
    success: function(response){
      var result = JSON.parse(response);
      document.getElementById('user_table_name').innerHTML = result.user;
      document.getElementById('user_table_password').innerHTML = result.password;
    },
    error: function(response){
      console.log("Bwahaha Thomas, you have thwarted yourself once again");
    }
  });
}

function make_user_stock_table(response){
  var table = document.getElementById('user_stock_table');
  var result = JSON.parse(response);
  var length = Object.keys(result).length;
  console.log(result);
  for(var i=0; i< length; i++){
    var table_row = document.createElement('tr');
    var new_stock = document.createElement('td');
    new_stock.innerHTML = Object.keys(result)[i];
    console.log(result[i]);
    table_row.appendChild(new_stock);
    table.appendChild(table_row);
  }

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
