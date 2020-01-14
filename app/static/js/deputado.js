$(document).ready(function(){
  loadVotingPresence();
  $("[id^='event-leg-']").on('click', function(){
    let thisId =  $(this).attr('id').split('-');
    thisId = thisId[thisId.length -1];
    displayNoneCharts();
    $('#eventPrecencesChart'+thisId).attr('style', 'display:initial');
  });
  loadExpensesHistory();
  loadDeputyAuthorships();

});

function displayNoneCharts()
{
  $("[id^='eventPrecencesChart']").attr('style', 'display:none');
}

function loadVotingPresence()
{
  let depId = window.location.href.split("=")[1];
  $.ajax({
      type: 'POST',
      url: '/deputy_event_presence',
      data:{'depId': depId},
      success: function(response){
        let eventPresences = response.eventPresences
        let legislatures = Object.keys(eventPresences)
        for(iterator=0; iterator<legislatures.length; iterator++)
        {
          $('#event-leg-'+legislatures[iterator]).prop("disabled", false);
          let allEvents = [];
          let allPresences = [];
          let allAverages = [];
          let eventNames = Object.keys(eventPresences[legislatures[iterator]]);
          for(iterator2=0; iterator2<eventNames.length; iterator2++)
          {
            allEvents.push(eventPresences[legislatures[iterator]][eventNames[iterator2]]['all-events'])
            allPresences.push(eventPresences[legislatures[iterator]][eventNames[iterator2]]['presence'])
            allAverages.push(eventPresences[legislatures[iterator]][eventNames[iterator2]]['mean-presence'])
          }
          generateVotingPresenceChart('eventPrecencesChart'+String(legislatures[iterator]), eventNames, allEvents, allPresences, allAverages);
        }
        $('#eventPrecencesChart'+String(legislatures[0])).attr('style', 'display:initial');
      },
      error: function(error){
          console.log(error);
      }
  });
}

function loadExpensesHistory()
{
  let depId = window.location.href.split("=")[1];
  $.ajax({
    type: 'POST',
    url: '/deputy_expenses_history',
    data: {'depId': depId},
    success: function(response){
      console.log(response);
      expensesHistory = response.expensesHistory;
      years = Object.keys(expensesHistory);
      for(iterator=0; iterator<years.length; iterator++)
      {
        let divId = 'expensesHistoryChart'+String(years[iterator]);
        $('#expensesChartArea').append(`<div id="${divId}"></div>`);
        generateExpensesHistoryChart(divId, years[iterator], expensesHistory[years[iterator]]['deputy_expenses'], expensesHistory[years[iterator]]['range']);
      }
      $('#expensesHistoryChart'+String(years[0])).attr('style', 'display:initial');
    },
    error: function(error){
      console.log(error);
    }
  });
}

function loadDeputyAuthorships()
{
  let depId = window.location.href.split("=")[1];
  $.ajax({
    type: 'POST',
    url: '/deputy_authorships',
    data: {'depId': depId},
    success: function(response){
      console.log(response);
    },
    error: function(error){
      console.log(error);
    }
  });
}

// PLOT FUNCTIONS ===================================================================================================
function generateVotingPresenceChart(chartDivId, eventNames, allEvents, allPresences, allAverages)
{
  Highcharts.chart(chartDivId, {
    chart: {
        type: 'column'
    },
    title: {
        text: 'Presenças em Votações Nominais'
    },
    xAxis: {
        categories: eventNames
    },
    yAxis: [{
        min: 0,
        title: {
            text: 'Votações'
        }
    }],
    legend: {
        shadow: false
    },
    tooltip: {
        shared: true
    },
    plotOptions: {
        column: {
            grouping: false,
            shadow: false,
            borderWidth: 0
        }
    },
    series: [{
        name: 'Quantidade de reuniões',
        color: 'rgba(165,170,217,1)',
        data: allEvents,
        pointPadding: 0.3,
        pointPlacement: 0.0
    }, {
        name: 'Quantidade de presenças',
        color: 'rgba(126,86,134,1)',
        data: allPresences,
        pointPadding: 0.3,
        pointPlacement: 0.0
    }, {
        name: 'Presença média',
        color: 'rgba(128, 127, 159,1)',
        data: allAverages,
        pointPadding: 0.3,
        pointPlacement: 0.0
    }]
  });
}

function generateExpensesHistoryChart(chartDivId, year, expenses, range)
{
  Highcharts.chart(chartDivId, {

    title: {
        text: 'Gastos em' + String(year)
    },

    xAxis: {
        type: 'datetime',
        accessibility: {
            rangeDescription: 'Range: Jul 1st 2009 to Jul 31st 2009.'
        }
    },

    yAxis: {
        title: {
            text: null
        }
    },

    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'R$'
    },

    series: [{
        name: 'Gastos',
        data: expenses,
        zIndex: 1,
        marker: {
            fillColor: 'white',
            lineWidth: 2,
            lineColor: Highcharts.getOptions().colors[0]
        }
    }, {
        name: 'Intervalo',
        data: range,
        type: 'arearange',
        lineWidth: 0,
        linkedTo: ':previous',
        color: Highcharts.getOptions().colors[0],
        fillOpacity: 0.3,
        zIndex: 0,
        marker: {
            enabled: false
        }
    }]
  });
}
