(function($) {

    $(document).ready(function() {

        var $loading = $('.loading').fadeIn('fast'),
            $win = $(window),
            $main = $('#main');

        function getPos($link, type) {
            var win = (type == 'width') ? $win.width() : $win.height();
            return parseInt((win / 2) - ((parseInt($link.data(type)) + 40) / 2), 10);
        }

        function loadImage($overlay, $link) {

            var $gif = $overlay.children('img')
                    .hide()
                    .attr('src', $link.attr('href'));

            $.merge($gif, $overlay)
                .animate({
                    width: $link.data('width') + 'px',
                    height: $link.data('height') + 'px',
                    left: getPos($link, 'width'),
                    top: getPos($link, 'height')
                });

            $gif.imagesLoaded(function() {
                    $gif.fadeIn('fast');
                });

        }

        function thumbClick(link) {

            var $link = $(link),
                $overlay = $('<div/>')
                    .addClass('overlay')
                    .css({
                        position: 'absolute',
                        width: $link.data('width')+'px',
                        height: $link.data('height')+'px'
                    })
                    .appendTo('body')
                    .overlay({
                        load: true,
                        left: getPos($link, 'width'),
                        top: getPos($link, 'height'),
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
                .attr('width', $link.data('width'))
                .attr('height', $link.data('height'))
                .click(function() {
                    $link = $link.parent().next().children('a');
                    if ($link.size() == 0) {
                        $link = $items.filter(':first');
                    }
                    loadImage($overlay, $link);
                })
                .appendTo($overlay);

            return false;

        }

        var $items = $main.find('a')
            .click(function() { return thumbClick(this); });

        $main.imagesLoaded(function($images) {
            $main
                .masonry({
                    itemSelector: 'li',
                    columnWidth: 25
                })
            $loading
                .fadeOut('fast', function() {
                    $main.find('li')
                        .fadeIn();
                    $('#main').infinitescroll({
                        navSelector: '.next',
                        nextSelector: '.next',
                        itemSelector: '#main li',
                        bufferPx: 100,
                        loading: {
                            finishedMsg: null,
                            img: '/static/img/loading.gif',
                            msg: null,
                            msgText: '',
                        },
                        pathParse: {
                            join: function(page) {
                                return '/' + page
                            }
                        }
                    },
                    function(items) {
                        var $items = $(items)
                            .addClass('show')
                            .hide();
                        $items.find('a')
                            .click(function() { return thumbClick(this); });
                        $items.imagesLoaded(function() {
                            $main.masonry('appended', $items, true);
                            $items.fadeIn('fast');
                        });
                    });

                });

        });

    });

})(jQuery);
