$(document).ready(function(){
  loadVotingPresence();
  loadExpensesHistory();
  loadDeputyAuthorships();

});

function initEventListener(btnIdPrefix, targetDivPrefix)
{
  $(`[id^='${btnIdPrefix}']`).on('click', function(){
    let thisId =  $(this).attr('id').split('-');
    thisId = thisId[thisId.length -1];
    displayNoneCharts(targetDivPrefix);
    $(`#${targetDivPrefix}`+thisId).attr('style', 'display:initial');
  });
}

function displayNoneCharts(targetDivPrefix)
{
  $(`[id^='${targetDivPrefix}']`).attr('style', 'display:none');
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
          generateVotingPresenceChart('eventPrecencesChart'+String(legislatures[iterator]), String(legislatures[iterator]), eventNames, allEvents, allPresences, allAverages);
        }
        $('#eventPrecencesChart'+String(legislatures[0])).attr('style', 'display:initial');
        initEventListener('event-leg-', 'eventPrecencesChart');
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
      let authorships = response.authorships;
      let legislatures = Object.keys(authorships);
      let authorshipButtonGroup = $('<div class="btn-group" />');
      for(iterator=0; iterator<legislatures.length; iterator++)
      {
        // creating the button to select this instance
        authorshipButtonGroup.append(`
        <button class="btn btn-dark" 
          type="button" 
          name="select-authorship-${legislatures[iterator]}" 
          id="authorship-leg-${legislatures[iterator]}">Legislatura ${legislatures[iterator]}</button>`);
        // populating with data
        let divId = 'deputyAuthorship'+String(legislatures[iterator]);
        $('#authorshipArea').append(`<div id="${divId}" class="row"></div>`);
        generateAuthorshipContainer(divId, legislatures[iterator], authorships[legislatures[iterator]]['authoring'], authorships[legislatures[iterator]]['median-authoring']);
      }
      for(iterator=1; iterator<legislatures.length; iterator++)
      {
          $('#deputyAuthorship'+String(legislatures[iterator])).attr('style', 'display:none');
      }
      $('#authorship-legislature-select').append(authorshipButtonGroup);
      initEventListener('authorship-leg-', 'deputyAuthorship');
    },
    error: function(error){
      console.log(error);
    }
  });
}


function generateAuthorshipContainer(divId, legislature, authoring, megianAuthoring)
{
  $('#'+divId).append(
    `<div class='col-sm-6 authorship-left-block'>
      <div class='container'>
        <div class='row'>
          <div class='col-sm-12'>
            <p class='authoringNumber'>${authoring}</p>
          </div>
        </div>
      </div>
      <div class='container'>
        <div class='row'>
          <div class='col-sm-12'>
            <p class='authoringDescription'>Essa é a quantidade de proposições nas quais o deputado participou
            como autor durante a legislatura ${legislature}.</p>
          </div>
        </div>
      </div>
    </div>

    <div class='col-sm-6 authorship-right-block'>
      <div class='container'>
        <div class='row'>
          <div class='col-sm-12'>
            <p class='medianAuthoringNumber'>${megianAuthoring}</p>
          </div>
        </div>
      </div>
      <div class='container'>
        <div class='row'>
          <div class='col-sm-12'>
            <p class='medianAuthoringDescription'>Essa é a mediana de participações em autorias durante o mesmo período.</p>
          </div>
        </div>
      </div>
    </div>`
  );
}

// PLOT FUNCTIONS ===================================================================================================
function generateVotingPresenceChart(chartDivId, legislature, eventNames, allEvents, allPresences, allAverages)
{
  Highcharts.chart(chartDivId, {
    chart: {
        type: 'column'
    },
    title: {
        text: 'Presenças em Votações Nominais na Legislatura '+legislature
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
