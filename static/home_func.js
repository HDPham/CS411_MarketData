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
  $.ajax({
    url:'/most_popular',
    type: 'GET',
    success: function(response){
      document.getElementById('stock_output').value = response;
    },
    error: function(response){
      document.getElementById('compare_stock_result').value = 'Sorry Hung, there was an error in your SQL :/ ';
    }
  });
}
