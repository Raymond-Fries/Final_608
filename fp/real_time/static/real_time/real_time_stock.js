
var socket = new WebSocket("ws://localhost:8000/ws/real_time/");

socket.onmessage = function(event) {
  var data =  JSON.parse(event.data);
    if(data.message.type === 'intraday_message'){
      if (document.getElementById("id_company_select").value === data.message.text.symbol){
          addData(stock_Chart,new Date(data.message.text.timestamp),data.message.text.close);
        }
    } else if(data.message.type === 'transaction_message' ){
        add_transactions_row(data.message.text.symbol,
                              new Date(data.message.text.timestamp),
                              data.message.text.side,data.message.text.quantity,
                              data.message.text.price,data.message.text.position_quantity);
        transactions_count();

     } else if (data.message.type === 'position_message'){
        position_table_manipulation(data.message.text.symbol,data.message.text.side,
                              data.message.text.pos_quantity,data.message.text.average_price,
                              data.message.text.cost);
     }else if(data.message.type === 'account_message' ){
        ptd = data.message.text.account
        update_profits_table(ptd);
    }
  }

////////////
/////////// FUNCTIONS SECTION
//////////


function roundingup(v, n) {
    return Math.ceil(v * Math.pow(10, n)) / Math.pow(10, n);
}

function add_transactions_row(symbol,timestamp,side,qty_bought,avg_price,pos_quantity){
  let the_table = document.querySelector('.transactionsTableBody');

  if(pos_quantity === 0){

      let row = the_table.insertRow(0);
      let cell0 = row.insertCell(0);
      let cell1 = row.insertCell(1);
      let cell2 = row.insertCell(2);
      let cell3 = row.insertCell(3);
      let cell4 = row.insertCell(4);
      let cell5 = row.insertCell(5);

      cell0.innerHTML = symbol;
      cell1.innerHTML = timestamp.getHours()+':'+timestamp.getMinutes()+':'+timestamp.getSeconds();
      cell2.innerHTML = ' ';
      cell3.innerHTML = qty_bought;
      cell4.innerHTML = roundingup(avg_price,3);
      cell5.innerHTML = pos_quantity;
  }else{
    let row = the_table.insertRow(0);
    let cell0 = row.insertCell(0);
    let cell1 = row.insertCell(1);
    let cell2 = row.insertCell(2);
    let cell3 = row.insertCell(3);
    let cell4 = row.insertCell(4);
    let cell5 = row.insertCell(5);

    cell0.innerHTML = symbol;
    cell1.innerHTML = timestamp.getHours()+':'+timestamp.getMinutes()+':'+timestamp.getSeconds();
    cell2.innerHTML = side;
    cell3.innerHTML = qty_bought;
    cell4.innerHTML = roundingup(avg_price,3);
    cell5.innerHTML = pos_quantity;
  }
}

function position_table_manipulation(symbol,side,quantity,avg_price,cost){
  let the_table = document.getElementById('positionsTableBody');
  let mr = get_matching_row(symbol);

  the_table.rows[mr].cells[1].innerHTML = side;
  the_table.rows[mr].cells[2].innerHTML = quantity;
  the_table.rows[mr].cells[3].innerHTML = roundingup(avg_price,3);
  the_table.rows[mr].cells[4].innerHTML = roundingup(cost,3);

  }
function transactions_count() {
    let count = parseInt(document.getElementById('t_counts').innerHTML);
    if (isNaN(count)!= true){
      document.getElementById('t_counts').innerHTML = count + 1;
    }else{
      let table = document.getElementById('transactionsTableBody');
      let number = table.rows.length;
      let number2 = number + 1;
      document.getElementById('t_counts').innerHTML = number2;
    }
  }

function get_matching_row(symbol){
  var table = document.getElementById('positionsTableBody');
  var msg = "No match"
  for(i=0;i<table.rows.length;i++){
    if(table.rows[i].cells[0].innerHTML===symbol){
      msg = i;
      break;
    }
  }
  return msg;
}

function update_profits_table(data){
  let the_table = document.querySelector(".profitsTableBody");

  the_table.rows[0].cells[0].innerHTML = data.cash;
  the_table.rows[0].cells[1].innerHTML = data.buying_power;
  the_table.rows[0].cells[2].innerHTML = Number(data.equity_now) - Number(data.beginning_equity);
}
/////////Initial transaction count//////
transactions_count()
