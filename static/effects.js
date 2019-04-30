// function call_update(){
//   var stock = document.getElementById('current_stock').value;
//   console.log(stock);
//   if(current_stock == null){
//     document.getElementById('stock_output').value = 'Sorry, you haven\'t selected any stock.';
//   }
//   $.ajax({
//     url:'/manual_update',
//     type: 'GET',
//     data: {
//       stock: stock,
//     }
//     success: function(response){
//       // Put values up on screen
//       document.getElementById("stock_output").value = Object.entries(response);
//       var values = Object.values(response); var keys = Object.keys(response);
//       var prices = []; var times = [];
//       //Keys and values are backwards, so reverse
//       keys = keys.reverse();
//       values = values.reverse();
//       // We only care about close, so cutting it down to just that
//       for(var i=0; i < keys.length; i++){
//         times.push(keys[i]);
//         prices.push(values[i][3]);
//       }
//       // package into a niiiiice data format
//       var data = [
//       {
//         x: times,
//         y: prices,
//         type: 'scatter'
//       }
//       ];
//       Plotly.newPlot('stockGraph', data, {}, {showSendToCloud: true});
//     },
//     error: function(response){
//       document.getElementById("stock_output").value = "Sorry, something went wrong in your search :/ Please make sure your stock symbol is valid";
//       document.getElementById('current_stock').value = null;
//     }
//   });
// }
