// This is for able to see chart. We are using Apex Chart. U can check the documentation of Apex Charts too..
var options = {
  series: [{
    name: 'Total Budget',
    data: [10000, 10000, 10000, 10000, 10000, 10000, 10000]
  }, {
    name: 'Expenditure',
    data: [5553, 8832, 7633, 10052, 12513, 8944, 732]
  }],
  chart: {
    type: 'area',
    height: 400
  },
  dataLabels: {
    enabled: false
  },
  colors: ['#33b2df', '#3e7d06'],
  stroke: {
    curve: 'straight'
  },
  markers: {
    size: 5,
    hover: {
      size: 9
    }
  },
  xaxis: {
    categories: ['Jan-22', 'Feb-22', 'Mar-22', 'Apr-22', 'May-22', 'Jun-22', 'Jul-22'],
  },
};

var chart = new ApexCharts(document.querySelector("#apex1"), options);
chart.render();


var options = {
  series: [44, 55, 2, 17, 15, 44],
  chart: {
  type: 'donut',
  height: 400
},
labels: ['Food', 'Travelling', 'Groceries', 'Medicine', 'Bills', 'Others'],
responsive: [{
  breakpoint: 480,
  options: {
    chart: {
      width: 200
    },
    legend: {
      position: 'bottom'
    }
  }
}]
};

var chart = new ApexCharts(document.querySelector("#apex2"), options);
chart.render();

// Sidebar Toggle Codes;

var sidebarOpen = false;
var sidebar = document.getElementById("sidebar");
var sidebarCloseIcon = document.getElementById("sidebarIcon");

function toggleSidebar() {
  if (!sidebarOpen) {
    sidebar.classList.add("sidebar_responsive");
    sidebarOpen = true;
  }
}

function closeSidebar() {
  if (sidebarOpen) {
    sidebar.classList.remove("sidebar_responsive");
    sidebarOpen = false;
  }
}


// Radial chart

var options = {
  series: [55, 44],
  chart: {
    height: 400,
    type: 'radialBar',
  },
  plotOptions: {
    radialBar: {
      dataLabels: {
        name: {
          fontSize: '20px',
        },
        value: {
          fontSize: '30px',
        },
        total: {
          show: true,
          label: 'Expenditure',
          formatter: function (w) {
            // By default this function returns the average of all series. The below is just an example to show the use of custom formatter function
            return 55 + '%'
          }
        }
      }
    }
  },
  labels: ['Expenditure', 'Time passed'],
};

var chart = new ApexCharts(document.querySelector("#target1"), options);
chart.render();


// cumulative_expenditure_day_wise_MTD
cumulative_expenditure_day_wise_MTD = JSON.parse(document.getElementById("target2-data1")
  .getAttribute('cumulative_expenditure_day_wise_mtd'))
cumulative_expected_expenditure_day_wise = JSON.parse(document.getElementById("target2-data2")
  .getAttribute('cumulative_expected_expenditure_day_wise'))
console.log('cumulative_expected_expenditure_day_wise', cumulative_expected_expenditure_day_wise)
var options = {
  series: [{
    name: 'Expected expenditure',
    data: cumulative_expected_expenditure_day_wise
  },
  {
    name: 'Actual expenditure',
    type: 'line',
    data: cumulative_expenditure_day_wise_MTD
  }],
  chart: {
    height: 400,
    type: 'area',
  },
  dataLabels: {
    enabled: false
  },
  colors: ['#33b2df', '#3e7d06'],
  stroke: {
    curve: 'straight'
  },
  markers: {
    size: 5,
    hover: {
      size: 9
    }
  },
  xaxis: {
    categories: Array.from({length: 30}, (_, i) => i + 1)
  },
  tooltip: {
    x: {
      format: 'dd/MM/yy HH:mm'
    },
  },
};

var chart = new ApexCharts(document.querySelector("#chart"), options);
chart.render();

var chart = new ApexCharts(document.querySelector("#target2"), options);
chart.render();


// Get the modal
var modal = document.getElementById("myModal");
    
// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("modal-close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}
