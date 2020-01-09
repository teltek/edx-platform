var total = 0;
var componentsTotal = 0;

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

function scaleElementsIframes(element, size) {
    if (element) {
        try {
            $(element).each(function(d){
                var iframed = $(element[d]);
                scaleElementSize(iframed, size);
            });
        } catch (e) {
        }
    }
}

function scaleAllIframes(size)
{
    var opencastIframes = $('iframe[id="mh_iframe"]');
    var uvigoIframes = $('iframe[src*="tv.uvigo.es"]');
    var cmarIframes = $('iframe[src*="tv.campusdomar.es"]');

    scaleElementsIframes(opencastIframes, size);
    scaleElementsIframes(uvigoIframes, size);
    scaleElementsIframes(cmarIframes, size);
}

function scaleIframesWhenLoaded() {
    opencastElement = $('body', $('#mh_iframe'));
    monostreamElement = $('body', $('iframe'));
    if (!opencastElement.context[0] && !monostreamElement.context[0]) {
        if (total < 10000) {
            total += 500;
            setTimeout(scaleIframesWhenLoaded, 500);
            return;
        }
    } else {
        total = 0;
        scaleAllIframes(0);
    }
}

function defineListener() {
    var pumukitButton = $('.single-template.add-xblock-component-button[data-type=pumukit]');
    if (pumukitButton.length != 1) {
        if (componentsTotal < 10000) {
            componentsTotal += 500;
            setTimeout(defineListener, 500);
            return;
        }
    } else {
        $('.single-template.add-xblock-component-button[data-type=pumukit]').click(function(e) {
            total = 0;
            setTimeout(scaleIframesWhenLoaded, 4000);
        });
    }
}

$(function(){
    total = 0;
    componentsTotal = 0;

    $(document).on('click', '.button.action-primary.action-save', function(e) {
        total = 0;
        setTimeout(scaleIframesWhenLoaded, 4000);
    });

    $(document).on('click', '.sequence-nav', function(e) {
	total = 0;
	setTimeout(scaleIframesWhenLoaded(), 500);
    });

    $(document).on('click', '.sequence-bottom', function(e) {
	total = 0;
	setTimeout(scaleIframesWhenLoaded(), 500);
    });

    $(window).on('resize', function(e){
        if (screen.width === window.innerWidth) {
            // Force fullscreen size scaling
            scaleAllIframes(1);
        } else {
            // Rescale iframes to fit in page
            try {
                scaleAllIframes(0);
            } catch (e) {
            }
        }
    });

    scaleIframesWhenLoaded();
    defineListener();
});
