
$(document).ready(function(){
  isLoadingTrue();
  loadDeputyListing();
  
  $('#btn-search-deputies').click(function(){

  });

});

function isLoadingTrue()
{
  $('#loadingArea').attr('display:block');
  $('.display-info').attr('style', 'display:none');
  
}

function isLoadingFalse()
{
  $('#loadingArea').attr('style', 'display:none');
  $('.display-info').attr('style', 'display:initial');

}
function loadDeputyListing()
{
   $.ajax({
       type: 'POST',
       url: '/deputy_listing',
       success: function(response){
         listDeputies(response.allDeputies);
       },
       error: function(error){
           console.log(error);
       }
   });
}


function listDeputies(deputyList)
{
  for(iterator = 0; iterator < deputyList.length; iterator ++)
  {
    currentDeputy = deputyList[iterator]
    $('#deputy-listing').append(
      `<div class="deputy-card" id="depId&${currentDeputy.ideCadastro}">
        <img class="deputy-img" src=${currentDeputy.urlFoto} alt="foto do(a) deputado(a) ${currentDeputy.nomeParlamentarAtual}">
        <div class="deputy-info-display">
          <span class="deputy-name-display">${currentDeputy.nomeParlamentarAtual}</span>
          <span class="deputy-uf-display">${currentDeputy.ufRepresentacaoAtual}</span>
          <span class="deputy-party-display">${currentDeputy.partidoAtual.sigla}</span>
        </div>
      </div>`
    );
  }
  $("[id^='depId']").on('click', function(){
    let thisId =  $(this).attr('id').split('&')[1];
    window.location.assign('/explorar/deputados/deputado?depId='+thisId);
  });
  isLoadingFalse();
}
