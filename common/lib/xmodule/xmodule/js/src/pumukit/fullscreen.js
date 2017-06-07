var total = 0;

function scaleElementSize(element, size) {
    var proportion = 1.00;
    var scaleProportion = 'scale(1.00)';
    var proportionWidth = $(element).parent().parent().parent().width() / $(element).width();
    if (size != 1 && proportionWidth < 1.00) {
        proportion = proportionWidth - 0.05;
        scaleProportion = 'scale('+proportion+')';
    }
    $(element).css('-ms-zoom', proportion);
    $(element).css('-moz-transform', scaleProportion);
    $(element).css('-moz-transform-origin', '0 0');
    $(element).css('-o-transform', scaleProportion);
    $(element).css('-o-transform-origin', '0 0');
    $(element).css('-webkit-transform', scaleProportion);
    $(element).css('-webkit-transform-origin', '0 0');
}

function scaleIframes() {
    el = $('body', $('#mh_iframe'));
    if (!el.context[0]) {
        if (total < 10000) {
            total += 500;
            setTimeout(scaleIframes, 500);
            return;
        }
    } else {
        total = 0;
        var iframes = $([id=mh_iframe])[0];
        $(iframes).each(function(d){
            var iframed = $(iframes[d]);
            scaleElementSize(iframed, 0);
        });
    }
}

$(function(){
    total = 0;

    $(document).on('click', '.button.action-primary.action-save', function(e) {
        total = 0;
        setTimeout(scaleIframes, 4000);
    });

    $(window).on('resize', function(e){
        if (screen.width === window.innerWidth) {
            // Force fullscreen size scaling
            var iframes = $([id=mh_iframe])[0];
            $(iframes).each(function(d){
                var iframed = $(iframes[d]);
                scaleElementSize(iframed, 1);
            });
        } else {
            // Rescale iframes to fit in page
            try {
                var iframes = $([id=mh_iframe])[0];
                $(iframes).each(function(d){
                    var iframed = $(iframes[d]);
                    scaleElementSize(iframed, 0);
                });
            } catch (e) {
            }
        }
    });

    scaleIframes();
});
