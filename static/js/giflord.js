(function($) {

    $(document).ready(function() {

        var $win = $(window),
            $main = $('#main');

        function getPos($link, type) {
            var win = (type == 'width') ? $win.width() : $win.height();
            return parseInt((win / 2) - ((parseInt($link.data(type)) + 40) / 2), 10);
        }

        function load($link) {
            var hash = /^\/image\/(\d+)\.gif$/g.exec($link.attr('href').trim());
            if (hash !== null) {
                $.history.load(hash[1]);
            }
            return false;
        }

        function loadItems($items) {
            $items
                .each(function(i, item) {
                    var $item = $(item);
                    $item.imagesLoaded(function() {
                        $item.fadeIn('slow');
                    });
                })
                .children('a')
                    .click(function() { return load($(this)); });
        }

        $main
            .masonry({
                itemSelector: 'li',
                columnWidth: 25
            });

        loadItems($main.find('li'));

        $main.imagesLoaded(function($images) {

            $('#main').infinitescroll({
                debug: false,
                navSelector: '.next',
                nextSelector: '.next',
                itemSelector: '#main li',
                bufferPx: 100,
                loading: {
                    finishedMsg: '',
                    img: '/static/img/loading.gif',
                    msgText: '',
                },
                pathParse: {
                    join: function(page) {
                        return '/' + page
                    }
                }
            },
            function(items) {
                var $items = $(items);
                loadItems($items);
                $main.masonry('appended', $items, true);
            });

            $.history.init(function(hash) {
                if (hash == '') {
                    return;
                }

                var $link = $main.find('a[href = "/image/'+hash+'.gif"]');
                if ($link.size() < 1) {
                    return;
                }

                var $overlay = $('.overlay');
                if ($overlay.size() > 0) {
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
                    return;
                }

                $link
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
                                $.history.load('');
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
                        return load($link);
                    })
                    .appendTo($overlay);

            },
            { unescape: ",/" });

        });

    });

})(jQuery);
