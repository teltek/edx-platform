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
	if ((inputPrice != 0) && (modePrice == 'audit')) {
	    $('#id_min_price').val(0);
	}
    });
    $(document).on('change paste keyup', '#id_min_price', function() {
	$('#message_price').remove();
	var inputPrice = parseInt($('#id_min_price').val());
	var modePrice = $('#id_mode_slug').val();
	var modeName = $("#id_mode_slug option[value='audit']").text();
	var message = '<p id="message_price">"'+modeName+'": 0.</p>';
	if ((inputPrice != 0) && (modePrice == 'audit')) {
	    $('#id_min_price').val(0);
	    $('.field-min_price').append(message);
	} else {
	    $('#message_price').remove();
	}
    });
    $('.field-mode_slug').each(function(e){
	var value = $(this).text();
	if (value == 'audit') {
	    $(this).text('Gratuito');
	} else if (value == 'honor') {
	    $(this).text('Credencial');
	} else if (value == 'verified') {
	    $(this).text('Certificado');
	}
    });
});
