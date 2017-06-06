$(document).ready(function(e) {
    $(window).on('resize', function(e){
        if (screen.width === window.innerWidth) {
            // this is full screen
            $('#mh_iframe').css('-ms-zoom', '1.00');
            $('#mh_iframe').css('-moz-transform', 'scale(1.00)');
            $('#mh_iframe').css('-moz-transform-origin', '0 0');
            $('#mh_iframe').css('-o-transform', 'scale(1.00)');
            $('#mh_iframe').css('-o-transform-origin', '0 0');
            $('#mh_iframe').css('-webkit-transform', 'scale(1.00)');
            $('#mh_iframe').css('-webkit-transform-origin', '0 0');
        } else {
            var proportion = ($('#mh_iframe').parent().parent().parent().width() / $('#mh_iframe').width()) - 0.05;
            var scaleProportion = 'scale('+proportion+')';
            $('#mh_iframe').css('-ms-zoom', proportion);
            $('#mh_iframe').css('-moz-transform', scaleProportion);
            $('#mh_iframe').css('-moz-transform-origin', '0 0');
            $('#mh_iframe').css('-o-transform', scaleProportion);
            $('#mh_iframe').css('-o-transform-origin', '0 0');
            $('#mh_iframe').css('-webkit-transform', scaleProportion);
            $('#mh_iframe').css('-webkit-transform-origin', '0 0');
        }
    });
});
                               
