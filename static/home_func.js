function search() {
  var stock = document.getElementById("searchbox").value;
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
      document.getElementById('current_stock').value = stock;
    },
    error: function(response){
      document.getElementById("stock_output").value = "Sorry, something went wrong in your search :/ Please make sure your stock symbol is valid";
      document.getElementById('current_stock').value = null;
    }
  });
}
function call_add_stock(){
  var current_stock = document.getElementById('current_stock').value;
  console.log(current_stock);
  if(current_stock==null){
    document.getElementById('stock_output').value = 'Sorry, you haven\'t selected any stock';
  }
  $.ajax({
    url:'/add_stock',
    type: 'POST',
    data: {
      stock: current_stock
    },
    success: function(response){
      console.log('success');
    },
    error: function(response){
      console.log('error');
    }
  });
}
function call_remove_stock(){
  var current_stock = document.getElementById('current_stock').value;
  console.log(current_stock);
  if(current_stock==null){
    document.getElementById('stock_output').value = 'Sorry, you haven\'t selected any stock';
  }
  $.ajax({
    url:'/remove_stock',
    type: 'POST',
    data: {
      stock: current_stock
    },
    success: function(response){
      console.log('success');
    },
    error: function(response){
      console.log('error');
    }
  });
}
function call_find_volatility(){
  var month = document.getElementById('month').value;
  var day = document.getElementById('day').value;
  var year = document.getElementById('year').value;

  console.log(month + " " + day + " " + year);
  $.ajax({
    url:'/find_volatility',
    type: 'GET',
    data:{
      month: month,
      day: day,
      year: year
    },
    success: function(response){
      document.getElementById('stock_output').value = response;
    },
    error: function(response){
      document.getElementById('compare_stock_result').value = 'Bwahaha Thomas, foiled by your own efforts!';
    }
  });
}

function call_most_popular(){
  var month = document.getElementById('month').value;
  var day = document.getElementById('day').value;
  var year = document.getElementById('year').value;

  $.ajax({
    url:'/most_popular',
    type: 'GET',
    data:{
      month: month,
      day: day,
      year: year
    },
    success: function(response){
      document.getElementById('stock_output').value = response;
    },
    error: function(response){
      document.getElementById('compare_stock_result').value = 'Sorry Hung, there was an error in your SQL :/ ';
    }
  });
}
