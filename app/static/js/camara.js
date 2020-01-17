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



    function initEventListener(btnIdPrefix, targetDivPrefix)
    {
      $(`[id^='${btnIdPrefix}']`).on('click', function(){
        let thisId =  $(this).attr('id').split('-');
        thisId = thisId[thisId.length -1];
        $(`[id^='${targetDivPrefix}']`).attr('style', 'display:none');
        if(targetDivPrefix != 'spentTotal')
          $(`#${targetDivPrefix}`+thisId).attr('style', 'display:initial')
        else
          $(`#${targetDivPrefix}`+thisId).attr('style', 'display:flex');
      });
    }



    /**
    function genderChart displays the gender comparisson graph
    param legislature - String indicating the current legislature of the data that will be displayed

    */

    function genderChart(legislature)
    {
      let genderChartResponse = JSON.parse(localStorage.getItem('genderResponse'));
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
              let professionData = response.professionData;
              let legislatures = Object.keys(professionData);
              professionButtonGroup = $('<div class="btn-group" />');

              for(iterator = 0; iterator<legislatures.length; iterator++)
              {
                professionButtonGroup.append(`
                <button class="btn btn-dark btn-time-select"
                  type="button"
                  name="select-profession-${legislatures[iterator]}"
                  id="profession-leg-${legislatures[iterator]}">Legislatura ${legislatures[iterator]}</button>`); 
                
                let divId = 'chamberProfession'+String(legislatures[iterator]);
                $('#professionChartData').append(`<div id="${divId}"></div>`);    

                generateprofessionChart(divId, legislatures[iterator], professionData[legislatures[iterator]]);

              }

              $('#chamberProfession'+String(legislatures[0])).attr('style', 'display:initial');
              $('#profession-select').append(professionButtonGroup);
              initEventListener('profession-leg-', 'chamberProfession');

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
              let schoolingData = response.schoolingData;
              let legislatures = Object.keys(schoolingData);
              let schoolingButtonGroup = $('<div class="btn-group" />');
              for(iterator = 0; iterator<legislatures.length; iterator++)
              {
                schoolingButtonGroup.append(`
                <button class="btn btn-dark btn-time-select"
                  type="button"
                  name="select-schooling-${legislatures[iterator]}"
                  id="schooling-leg-${legislatures[iterator]}">Legislatura ${legislatures[iterator]}</button>`); 
                
                let divId = 'chamberSchooling'+String(legislatures[iterator]);
                $('#schoolingChartData').append(`<div id="${divId}"></div>`);    

                generateSchoolingChart(divId, legislatures[iterator], schoolingData[legislatures[iterator]]);

              }

              $('#chamberSchooling'+String(legislatures[0])).attr('style', 'display:initial');
              $('#schooling-select').append(schoolingButtonGroup);
              initEventListener('schooling-leg-', 'chamberSchooling');
    
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
          valuesByState = response.data;
          legislatures = Object.keys(valuesByState);
          let valuesButtonGroup = $('<div class="btn-group" />');
          for(iterator=0;iterator<legislatures.length;iterator++)
          {
            // creating the time selection button
            valuesButtonGroup.append(`
            <button class="btn btn-dark btn-time-select"
              type="button"
              name="select-map-${legislatures[iterator]}"
              id="map-leg-${legislatures[iterator]}">Legislatura ${legislatures[iterator]}</button>`); 
              
              // creating the div element to render the chart
              let divId = 'valueMapChart'+String(legislatures[iterator]);
              $('#mapChartArea').append(`<div id="${divId}"></div>`);

              // calling the chart render function
              generateValueByStateChart(divId, legislatures[iterator], valuesByState[legislatures[iterator]]);
          }
          $('#valueMapChart'+String(legislatures[0])).attr('style', 'display:initial');
          $('#mapLegislatureSelect').append(valuesButtonGroup);
          initEventListener('map-leg-', 'valueMapChart');
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
            let totalSpent = response.allSpent;
            let legislatures = Object.keys(totalSpent);
            let spentButtonGroup = $('<div class="btn-group" />');
            for(iterator=0; iterator<legislatures.length; iterator++)
            {
              spentButtonGroup.append(`
              <button class="btn btn-dark btn-time-select"
                type="button"
                name="select-spent-${legislatures[iterator]}"
                id="spent-leg-${legislatures[iterator]}">Legislatura ${legislatures[iterator]}</button>`); 
                
              let divId = 'spentTotal'+String(legislatures[iterator]);
              $('#totalSpentContainer').append(`<div class="row spent-value" id=${divId} />`);

              generateTotalSpentContainer(divId, totalSpent[legislatures[iterator]])
            }
            $('#spentTotal'+legislatures[0]).attr('style', 'display:flex');
            $('#spentLegislatureSelect').append(spentButtonGroup);
            initEventListener('spent-leg', 'spentTotal');

        },
        error: function(error){
            console.log(error);
        }
    });
}





// chart functions ===========================================================

function generateprofessionChart(divId, legislature, data)
{
  Highcharts.chart(divId, {
    series: [{
        type: 'treemap',
        layoutAlgorithm: 'squarified',
        data: data
    }],
    title: {
        text: 'Profissões na Câmara na Legislatura '+ legislature
    },
    subtitle: {
        text: 'Frequência de cada profissão.'
    }
  });  
}


function generateSchoolingChart(divId, legislature, data)
{
  Highcharts.chart(divId, {
    chart: {
      type: 'funnel',
      height: '600'
    },
    title: {
      text: 'Escolaridade na Legislatura '+ legislature
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
        height:'500',
      }
    },
    legend: {
      enabled: true
    },
    series: [{
        name: 'Deputados',
        data: data
      }
    ]
  });

}

function generateValueByStateChart(divId, time, data)
{
  Highcharts.mapChart(divId, {
    chart: {
        map: 'countries/br/br-all'
    },
    title: {
        text: 'Cota Parlamentar por Estado na Legislatura '+time
    },
    subtitle: {
        text: 'Source map: <a href="http://code.highcharts.com/mapdata/countries/br/br-all.js">Brazil</a>'
    },
    series: [{
        data: data,
        showInLegend: false,
        states: {
            hover: {
                color: '#BADA55'
            }
        },
        dataLabels: {
            enabled: true,
            format: '{point.dname}'
        }
    }]
 });

}

function generateTotalSpentContainer(divId, totalSpent)
{
$(`#${divId}`).append(
  `<div class='col-sm-12'><p class='value-display'>${totalSpent}<p></div>`);
}