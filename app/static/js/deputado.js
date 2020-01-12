$(document).ready(function(){
  loadVotingPresence();
});

function loadVotingPresence()
{
  let depId = window.location.href.split("=")[1];
  $.ajax({
      type: 'POST',
      url: '/deputy_voting_presence',
      data:{'depId': depId},
      success: function(response){
        let votingPresences = response.votingPresences
        let legislatures = Object.keys(votingPresences)
        let allEvents = []
        let allPresences = []
        for(iterator=0; iterator<legislatures.length; iterator++)
        {
          allEvents.push(votingPresences[legislatures[iterator]]['all-events']);
          allPresences.push(votingPresences[legislatures[iterator]]['presence']);
        }
        generateVotingPresenceChart(legislatures, allEvents, allPresences);
      },
      error: function(error){
          console.log(error);
      }
  });
}

function generateVotingPresenceChart(legislatures, allEvents, allPresences)
{
  Highcharts.chart('votingPrecencesChart', {
    chart: {
        type: 'column'
    },
    title: {
        text: 'Presenças em Votações Nominais'
    },
    xAxis: {
        categories: legislatures
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
        name: 'Quantidade de votações',
        color: 'rgba(165,170,217,1)',
        data: allEvents,
        pointPadding: 0.3,
        pointPlacement: 0.0
    }, {
        name: 'Quantidade de presenças',
        color: 'rgba(126,86,134,.9)',
        data: allPresences,
        pointPadding: 0.4,
        pointPlacement: 0.0
    }]
  });
}
