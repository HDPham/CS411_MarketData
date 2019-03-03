function search() {
  var stock = document.getElementById("searchbox").value;
  console.log(stock)
  $.ajax({
    // send data to scraping.py
    url: '/scraper',
    type: 'GET',
    data: stock,
    dataType: "json",
    success: function(response){
      document.getElementById("stock_output").value = Object.values(response);
    },
    error: function(response){
      document.getElementById("stock_output").value = "Sorry, something went wrong in your search :/";
    }
  });
}
