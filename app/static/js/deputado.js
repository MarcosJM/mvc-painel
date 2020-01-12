$(document).ready(function(){
  loadVotingPresence();
  $("[id^='event-leg-']").on('click', function(){
    let thisId =  $(this).attr('id').split('-');
    thisId = thisId[thisId.length -1];
    displayNoneCharts();
    $('#eventPrecencesChart'+thisId).attr('style', 'display:initial');
  });


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
