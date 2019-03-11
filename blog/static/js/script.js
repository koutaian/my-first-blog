$(function() {
  $('.dependent').dependentSelects({
	  placeholderOption: ['群を選んでください', '授業を選んでください']
  });
  $("button").click(function() {
  });

  $(".plus").click(function() {
    $(".dependent").hide();
    $(".dependent-sub").hide();
    var id = $(this).attr("id");
    var idx = id.substr(4)
    $('#sec%'.replace("%", idx)).show()
    $("#save").show();
    $("#save").attr("class", idx);
  });

  $("#save").click(function() {
    idx = $(this).attr("class")
    var data = $('[name=choice%]'.replace("%", idx)).val();
    var text = $('[name=choice%] option:selected'.replace("%", idx)).text();
    $("#form%".replace("%", idx)).val(data);
    $("#text%".replace("%", idx)).text(text);
    $("h1").text($("input").val())
  });
});
