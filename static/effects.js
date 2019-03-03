


function search() {
  var stock_type = document.getElementById("searchbox").value
  var data_obj = {};
  data_obj.timestamp = $('#timestamp').val();
  data_obj.open = $('#open').val();
  data_obj.high = $('#high').val();
  data_obj.low = $('#low').val();
  data_obj.close = $('#close').val();
  data_obj.volume = $('#volume').val();
  $.ajax({
    // send data to scraping.py
    url: 'scraping.py',
    method: 'POST',
    data: JSON.stringify(data_obj)
    dataType: "json",
    success: function(response){
      console.log(response);
    },
    error: function(response){
      console.log(response);
    }
    // store JSON data and send it to textarea
  });
}
