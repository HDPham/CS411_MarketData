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
  var number_of = parseInt(document.getElementById('number_of_stocks').value);
  console.log(current_stock);
  console.log(number_of);
  if(isNaN(number_of)){
    document.getElementById('stock_output').value = 'Please selected a valid integer';
  }
  if(current_stock==null){
    document.getElementById('stock_output').value = 'Sorry, you haven\'t selected any stock';
  }
  $.ajax({
    url:'/add_stock',
    type: 'POST',
    data: {
      stock: current_stock,
      number_of: number_of
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

function call_update(){
  $.ajax({
    url:'/update',
    type: 'POST',
    success: function(response){
      console.log('success');
    },
    error: function(response){
      console.log('error, STOOPID');
    }
  });
}

// Inspiration and credit for code goes to Danny Pule on medium ; https://medium.com/@danny.pule/export-json-to-csv-file-using-javascript-a0b7bc5b00d2
function convert_to_csv(){
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
      var stock_data = JSON.stringify(response);
      var csv_str = '';
      for(var i=Object.entries(response).length-1; i>= Object.entries(response).length-500; i--){
        var row = '';
        row += JSON.stringify(Object.entries(response)[i][0])+",";
        for(var j=0; j <Object.entries(response)[i][1].length; j++){
          row+=JSON.stringify(Object.entries(response)[i][1][j])+",";
        }
        csv_str += row + '\r\n';
      }
      var csv_title = stock + '.csv';
      var obj = new Blob([csv_str], { type: 'text/csv;charset=utf-8;' });
      var link = document.getElementById('downloadable');
      var url = URL.createObjectURL(obj);
      link.setAttribute("href", url);
      link.setAttribute("download", csv_title);
    },
    error: function(response){
      document.getElementById("stock_output").value = "Sorry, something went wrong in your search :/ Please make sure your stock symbol is valid";
      document.getElementById('current_stock').value = null;
    }
  });
}

function simulation() {
  document.getElementById('error_msg').value = 'Robot Loading...';
  $.ajax({
    url: 'simulation',
    type: 'GET',
    data: {
      stock: $('#stocksim').val(),
      lavg: $('#lavg').val(),
      savg: $('#savg').val()
    },
    success: function(response) {
      document.getElementById('error_msg').value = 'Simulation success';
    },
    error: function(response) {
      document.getElementById('error_msg').value = 'Sorry, something went wrong';
    }
  });
}