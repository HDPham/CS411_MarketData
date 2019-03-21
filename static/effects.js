function search() {
  var stock = document.getElementById("searchbox").value;
  console.log(stock)
  $.ajax({
    // send data to scraping.py
    url: '/get_stock',
    type: 'GET',
    data: {
      stock: stock
    },
    dataType: "json",
    success: function(response){
      // Put values up on screen
      document.getElementById("stock_output").value = Object.entries(response);
      var values = Object.values(response); var keys = Object.keys(response);
      var prices = []; var times = [];
      //Keys and values are backwards, so reverse
      keys = keys.reverse();
      values = values.reverse();
      // We only care about close, so cutting it down to just that
      for(var i=0; i < keys.length; i++){
        times.push(keys[i]);
        prices.push(values[i][3]);
      }
      // package into a niiiiice data format
      var data = [
      {
        x: times,
        y: prices,
        type: 'scatter'
      }
      ];
      Plotly.newPlot('stockGraph', data, {}, {showSendToCloud: true});
    },
    error: function(response){
      document.getElementById("stock_output").value = "Sorry, something went wrong in your search :/ Please make sure your stock symbol is valid";
    }
  });
}

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
      }
      window.location.href = '/home/'+entries[1][1];
    },
    error: function(response){
      console.log('error');
      document.getElementById('error_msg').value = 'Sorry, something went wrong in processing your request'
    }
  });
}
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
      window.location.href = '/home/'+user;
    },
    error: function(response){
      console.log('error');
    }
  });
}
function set_user_for_home(){
  var user = document.getElementById('user_name').value;
  console.log(user);
  if(user == ''){
    user = 'Guest';
  }
  console.log(user);
  window.location.href = '/home/'+user;
}
