$(document).ready(function(){
    loadProfessions();
    loadValuesByState();
});

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
            console.log('erross')
            console.log(error);
        }
    });
}