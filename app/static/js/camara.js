$(document).ready(function(){
    loadGenderCount();
    loadProfessions();
    loadValuesByState();
    loadSchooling();
    loadTotalSpent();

    $("[id^='gender-leg-']").on('click', function(){
      let thisId =  $(this).attr('id').split('-');
      let legislature = thisId[thisId.length -1];
      if (legislature != undefined)
      {
        let genderChartResponse = localStorage.getItem('genderResponse');
        let getgenderChart = $('#genderChart').highcharts();
        getgenderChart.destroy();
        genderChart(legislature);
        $("#genderChart image")
          .attr('transform', 'translate(4,0)')
          .attr('width', '5');
      }
    });
});



    /**
    function genderChart displays the gender comparisson graph
    param legislature - String indicating the current legislature of the data that will be displayed

    */

    function genderChart(legislature)
    {
      let genderChartResponse = JSON.parse(localStorage.getItem('genderResponse'));
      console.log(genderChartResponse);
      Highcharts.chart('genderChart', {
        plotOptions: {
          column: {
            events: {
                legendItemClick: function () {
                    return false; // <== returning false will cancel the default action
                }
            }
          }
        },
        chart: {
            type: 'item',
        },

        title: {
            text: 'Highcharts item chart'
        },

        subtitle: {
            text: 'With image symbols'
        },
        legend: {
            enabled: false
        },

        series: [{
            name: '',
            layout: 'horizontal',
            data: [{
                y: genderChartResponse[legislature]['M'],
                marker: {
                  radius: '8',
                    symbol: 'url(data:image/svg+xml;base64,PHN2ZyBpZD0ibWFsZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB2aWV3Qm94PSIwIDAgMTkyIDUxMiI+PHBhdGggZD0iTTk2IDBjMzUuMzQ2IDAgNjQgMjguNjU0IDY0IDY0cy0yOC42NTQgNjQtNjQgNjQtNjQtMjguNjU0LTY0LTY0UzYwLjY1NCAwIDk2IDBtNDggMTQ0aC0xMS4zNmMtMjIuNzExIDEwLjQ0My00OS41OSAxMC44OTQtNzMuMjggMEg0OGMtMjYuNTEgMC00OCAyMS40OS00OCA0OHYxMzZjMCAxMy4yNTUgMTAuNzQ1IDI0IDI0IDI0aDE2djEzNmMwIDEzLjI1NSAxMC43NDUgMjQgMjQgMjRoNjRjMTMuMjU1IDAgMjQtMTAuNzQ1IDI0LTI0VjM1MmgxNmMxMy4yNTUgMCAyNC0xMC43NDUgMjQtMjRWMTkyYzAtMjYuNTEtMjEuNDktNDgtNDgtNDh6IiBmaWxsPSIjMkQ1RkYzIi8+PC9zdmc+)'
                },
                color: '#2D5FF3'
            }, {
                y: genderChartResponse[legislature]['F'],
                marker: {
                  radius: '8',
                    symbol: 'url(data:image/svg+xml;base64,PHN2ZyBpZD0iZmVtYWxlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTYgNTEyIj48cGF0aCBkPSJNMTI4IDBjMzUuMzQ2IDAgNjQgMjguNjU0IDY0IDY0cy0yOC42NTQgNjQtNjQgNjRjLTM1LjM0NiAwLTY0LTI4LjY1NC02NC02NFM5Mi42NTQgMCAxMjggMG0xMTkuMjgzIDM1NC4xNzlsLTQ4LTE5MkEyNCAyNCAwIDAgMCAxNzYgMTQ0aC0xMS4zNmMtMjIuNzExIDEwLjQ0My00OS41OSAxMC44OTQtNzMuMjggMEg4MGEyNCAyNCAwIDAgMC0yMy4yODMgMTguMTc5bC00OCAxOTJDNC45MzUgMzY5LjMwNSAxNi4zODMgMzg0IDMyIDM4NGg1NnYxMDRjMCAxMy4yNTUgMTAuNzQ1IDI0IDI0IDI0aDMyYzEzLjI1NSAwIDI0LTEwLjc0NSAyNC0yNFYzODRoNTZjMTUuNTkxIDAgMjcuMDcxLTE0LjY3MSAyMy4yODMtMjkuODIxeiIgZmlsbD0iI0YyM0EyRiIvPjwvc3ZnPg==)'
                },
                color: '#F23A2F'
            }]
        }]

      });
      // $('#genderChart').children().click(function(){
      //   $("#genderChart image")
      //     .attr('transform', 'translate(4,0)')
      //     .attr('width', '5');
      // });

    }

    function loadGenderCount()
    {
       $.ajax({
           type: 'POST',
           url: '/gender_count',
           success: function(response){
             localStorage.setItem('genderResponse', JSON.stringify(response));
             genderChart('55');
           },
           error: function(error){
               console.log(error);
           }
       });
    }

    function loadProfessions() {
        $.ajax({
            type: 'POST',
            url: '/professions',
            success: function(response){
                Highcharts.chart('chart', {
                    series: [{
                        type: 'treemap',
                        layoutAlgorithm: 'squarified',
                        data: response['data']
                    }],
                    title: {
                        text: 'Profissões na Câmara'
                    },
                    subtitle: {
                        text: 'Frequência de cada profissão.'
                    }
                });
            },
            error: function(error){
                console.log(error);
            }
        });
    };

    function loadSchooling() {
        $.ajax({
            type: 'POST',
            url: '/schooling',
            success: function(response){
               Highcharts.chart('schooling', {
                  chart: {
                    type: 'funnel',
                    height: '500'
                  },
                  title: {
                    text: 'Escolaridade'
                  },
                  plotOptions: {
                    funnel: {
                      depth: 100
                    },
                    series: {
                      dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b> <br/>{point.y:,.0f} ({point.yPercentage} %)',
                        softConnector: true,
                        crop: false
                      },
                      center: ['50%', '50%'],
                      neckWidth: '30%',
                      neckHeight: '25%',
                      width: '80%',
                    }
                  },
                  legend: {
                    enabled: true
                  },
                  series: [{
                      name: 'Deputados',
                      data: response['data']
                    }
                  ]
                });
            },
            error: function(error){
                console.log(error);
            }
        });
    };

    function loadValuesByState() {
        $.ajax({
            type: 'POST',
            url: '/values_by_state',
            success: function(response) {
                console.log(response);
                console.log('PASSEEEEEI');
                Highcharts.mapChart('map', {
                  chart: {
                    map: 'countries/br/br-all'
                  },
                  title: {
                    text: 'Highmaps basic demo'
                  },
                  subtitle: {
                    text: 'Source map: <a href="http://code.highcharts.com/mapdata/countries/br/br-all.js">Brazil</a>'
                  },
                  series: {
                    dataLabels: {
                      enabled: true,
                      format: '<b>{point.name}</b> <br/>{point.y:,.0f} ({point.yPercentage} %)',
                      softConnector: true,
                      crop: false
                    },
                    center: ['50%', '50%'],
                    neckWidth: '30%',
                    neckHeight: '25%',
                    width: '80%',
                  },
                  legend: {
                    enabled: true
                  },
                  series: [{
                    name: 'Deputados',
                    data: response['data']
                  }]
                });
        },
        error: function(error){
            console.log(error);
        }
    });
}

function loadValuesByState() {
    $.ajax({
        type: 'POST',
        url: '/values_by_state',
        success: function(response) {
            Highcharts.mapChart('map', {
            chart: {
                map: 'countries/br/br-all'
            },
            title: {
                text: 'Highmaps basic demo'
            },
            subtitle: {
                text: 'Source map: <a href="http://code.highcharts.com/mapdata/countries/br/br-all.js">Brazil</a>'
            },
            series: [{
                data: response['data'],
                showInLegend: false,
                states: {
                    hover: {
                        color: '#BADA55'
                    }
                },
                dataLabels: {
                    enabled: true,
                    format: '{point.name}'
                }
            }]
         });
        },
        error: function(error){
            console.log(error);
        }
    });
}

function loadTotalSpent() {
    $.ajax({
        type: 'POST',
        url: '/total_spent',
        success: function(response) {
            $('#total_spent').text(response['data']);
        },
        error: function(error){
            console.log(error);
        }
    });
}
