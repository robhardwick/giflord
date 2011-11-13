(function($) {

    function getPos(type, size) {
        if (type == 'left') {
            win = $(window).width();
        } else {
            win = $(window).height();
        }
        return ((win / 2) - ((size + 40) / 2));
    }

    function loadImage($overlay, $link) {

        var width = $link.data('width'),
            height = $link.data('height'),
            $gif = $overlay.children('.gif')
                .hide()
                .attr('src', $link.attr('href'))
                .imagesLoaded(function() {
                    $gif.fadeIn('fast');
                });

        $.merge($gif, $overlay)
            .animate({
                width: width + 'px',
                height: height + 'px',
                left: getPos('left', width) + 'px',
                top: getPos('top', height) + 'px'
            });

    }

    $(document).ready(function() {

        $('html').removeClass('no-js');

        var $loading = $('.loading').fadeIn('fast');

        var $main = $('#main');

        var $items = $main.children('a')
            .hide()
            .click(function() {

                var $link = $(this),
                    width = $link.data('width'),
                    height = $link.data('height');

                var $overlay = $('<div/>')
                    .addClass('overlay')
                    .css({
                        width: width,
                        height: height
                    })
                    .appendTo('body')
                    .overlay({
                        load: true,
                        left: getPos('left', width),
                        top: getPos('top', height),
                        mask: {
                            color: '#000',
                            opacity: 0.4,
                            loadSpeed: 200
                        },
                        onBeforeLoad: function(e) {
                            $link.css('boxShadow', 'none');
                        },
                        onClose: function(e) {
                            $overlay.remove();
                        }
                    });

                $('<img/>')
                    .attr('src', $link.attr('href'))
                    .attr('width', width)
                    .attr('height', height)
                    .addClass('gif')
                    .click(function() {
                        $link = $link.next();
                        if ($link.size() == 0) {
                            $link = $items.filter(':first');
                        }
                        loadImage($overlay, $link);
                    })
                    .appendTo($overlay);

                return false;

            });

        $main.imagesLoaded(function($images) {
            $main
                .masonry({
                    itemSelector : 'a',
                    columnWidth: 25
                })
            $items
                .fadeIn();
            $loading.fadeOut();
        });

    });

})(jQuery);
