$(document).ready(function (){
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
      document.getElementById('portfolio_results').innerHTML = "Stock: [Average daily return, price variance, std. dev. of price, covariance of stock with market, beta] "+ " " +response;
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
  var result = JSON.parse(response);
  console.log(result);
  var table = document.getElementById('user_tracked_stocks');
  console.log(table.children[1]);
  stock_number = 0;
  for(key in result) {
    console.log(key);
    var row = table.children[1].insertRow(-1);

    var cell1 = document.createElement('th');
    cell1.scope = "row";
    cell1.innerHTML = ++stock_number;
    row.appendChild(cell1);

    var cell2 = row.insertCell(-1);
    cell2.innerHTML = result[key][0].toUpperCase();

    var cell3 = row.insertCell(-1);
    cell3.innerHTML = result[key][1];
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
