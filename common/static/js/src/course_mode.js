$(function() {
    $(document).on('change', '#id_mode_slug', function() {
	var modePrice = parseInt($('#id_mode_slug').attr(this.value));
	var inputPrice = parseInt($('#id_min_price').val());
	var otherPrices = [];
	$("#id_mode_slug > option").each(function(){
	    otherPrices.push(parseInt($('#id_mode_slug').attr(this.value)));
	});
	if (-1 != otherPrices.indexOf(inputPrice)) {
	    $('#id_min_price').val(modePrice);
	}
    });
});
