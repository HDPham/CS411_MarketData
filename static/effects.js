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
      document.getElementById("stock_output").value = Object.entries(response);
    },
    error: function(response){
      document.getElementById("stock_output").value = "Sorry, something went wrong in your search :/ Please make sure your stock symbol is valid";
    }
  });
}
