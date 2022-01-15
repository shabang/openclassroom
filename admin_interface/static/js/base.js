$("#id_proprietaire").change(function () {
    var url = $("#sejourForm").data("animals-url");  // get the url of the `load_animals` view
    var proprietaireId = $(this).val();  // get the selected proprietaire ID from the HTML input
    $.ajax({                       // initialize an AJAX request
        url: url,                    // set the url of the request (= localhost:8000/hr/ajax/load-animals/)
        data: {
          'proprietaire': proprietaireId       // add the proprietaire id to the GET parameters
        },
        success: function (data) {   // `data` is the return of the `load_animals` view function
          $("#id_animaux").html(data);  // replace the contents of the proprietaire input with the data that came from the server
        }
    });
});

$('#sejourForm').on('change', '*', function(event) {
    var champs = ['commentaire','montant','montant_restant','proprietaire'];
    if (champs.indexOf(event.target.name)==-1){
        var url = $("#sejourForm").data("calcul-montant-url");
        $.post(url,$('#sejourForm').serialize(),function (data){
            $("#id_montant").val(data["montant"]);
            $("#id_montant_restant").val(data["montant_restant"]);
            $("#calcul").html(data["calcul"]);
        });
    }
 });

 $("select#id_longue_duree").change(function () {
  var value = $(this).val();
  var fields = $(
    'input[name="montant_jour_longue_duree"],label[for="id_montant_jour_longue_duree"]'
  );
  switch (value) {
    case "OUI":
      fields.show();
      break;
    case "NON":
      fields.hide();
      break;
  }
});

document.addEventListener("DOMContentLoaded", function () {
  var value = $("select#id_longue_duree").val();

  var fields = $(
    'input[name="montant_jour_longue_duree"],label[for="id_montant_jour_longue_duree"]'
  );
  switch (value) {
    case "OUI":
      fields.show();
      break;
    case "NON":
      fields.hide();
      break;
  }
});