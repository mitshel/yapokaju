(function ($, window, document, undefined) {
    'use strict';
    var pluginName = "sitePlugin",
        defaults = {
            sliderFx: 'crossfade',		// Slider effect. Can be 'slide', 'fade', 'crossfade'
            sliderInterval: 6000,		// Interval
            speedAnimation: 600,        // Default speed of the animation
            countdownTo: '2017/09/16',          // Change this in the format: 'YYYY/MM/DD'
            successText: 'You have successfully subscribed', // text after successful subscribing
            errorText: 'Please, enter a valid email', // text, if email is invalid
            tooltipPosition: 'bottom',            // Tooltip position
            scrollTopButtonOffset: 100 // when scrollTop Button will show
        },
        $loc = $(location),
        $win = $(window),
        $doc = $(document),
        $html = $('html'),
        onMobile = false,
        scrT;

    // The plugin constructor
    function Plugin(element, options) {
        var that = this;
        that.element = $(element);
        that.options = $.extend({}, defaults, options);

        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
            onMobile = true;
        }

        that.init();

        // onLoad function
        $win.ready(function () {
            that.activate();

        }).scroll(function () {  // onScroll function

        }).resize(function () {  // onResize function

        });

    }

    Plugin.prototype = {
        init: function () {
            this.body = $(document.body);

            this.upcomingEventsSection = $('.section-upcoming-events');
        },
        activate: function () {
            var instance = this;

            if (instance.upcomingEventsSection.length > 0) {
                instance.upcomingEventsSection.find('.tabs').each(function (idx, element) {
                    var $element = $(element);

                    $element.easytabs({
                        animate: false,
                        tabs: 'div > ul > li',
                    });
                });
            }
        },

    };

    $.fn[pluginName] = function (options) {
        return this.each(function () {
            if (!$.data(this, "plugin_" + pluginName)) {
                $.data(this, "plugin_" + pluginName, new Plugin(this, options));
            }
        });
    };
})(jQuery, window, document);