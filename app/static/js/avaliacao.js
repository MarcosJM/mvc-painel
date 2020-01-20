let ranges;
$(document).ready(function(){
  ranges = document.querySelectorAll("[id^=range-]");
  initRangeSliders();
  $('#anchor-ranking-page').click(
    function()
    {
      window.location.assign('/explorar/avaliacao/ranking');
    }
  );
});

function initRangeSliders()
{
  for(let iterator=0; iterator<ranges.length; iterator++)
  {
    thisId = ranges[iterator].id.split('-');
    thisId = thisId[thisId.length -1];
    $('#text-'+thisId).attr('value', ranges[iterator].value);
  }
  limitRangeSliders();
}

function limitRangeSliders()
{
  $('[id^="range-"]').on('input', function(){
    let rangeValues = 0;
    for(let iterator=0; iterator<ranges.length; iterator++)
    {
      rangeValues+=parseInt(ranges[iterator].value);
    }
    if(rangeValues >= 101)
    {
      let newVal = 0;
      $('[id^="range-"]').not(this).each(function () {
        newVal += parseInt($(this).val());
      });
      $(this).val(100 - newVal);
    }
    thisId = $(this).attr('id').split('-');
    thisId = thisId[thisId.length -1];
    $('#text-'+thisId).attr('value', $(this).val());
  
  });

}