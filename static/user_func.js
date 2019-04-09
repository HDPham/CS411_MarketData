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

function call_portfolio_calculator(){
  $.ajax({
    url:'/portfolio_calculator',
    type: 'GET',
    success: function(response){
      document.getElementById('portfolio_results').innerHTML = response;
    },
    error: function(response){
      console.log('error');
    }
  });
}

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
  var result = response;
  console.log(result);
  var table = document.getElementById('user_tracked_stocks');
  console.log(table.children[1]);
  for(i in result) {
    var row = table.children[1].insertRow(-1);
    var cell1 = document.createElement('th');
    cell1.scope = "row";
    cell1.innerHTML = 1 + parseInt(i);
    row.appendChild(cell1);
    var cell2 = row.insertCell(-1);
    cell2.innerHTML = result[i].toUpperCase();

  }
  console.log(table);
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
