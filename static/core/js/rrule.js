(function ($) {
    var $repeatTypeElement,
        $intervalDailyElement,
        $intervalWeeklyElement,
        $repeatWeeklyDayElement,
        $intervalMonthlyElement,
        $repeatMonthlyDayElement,
        $repeatMonthlyDateElement,
        $intervalYearlyElement,
        $repeatYearlyMonthElement,
        $rruleElement,
        $freqTypeElement,
        $freqCountElement;

    var methods = {
        init: function (options) {
            var settings = $.extend({
                prefix: '',
            }, options);

            $rruleElement = $('#' + settings['prefix'] + 'rrule');
            $repeatTypeElement = $('#' + settings['prefix'] + 'repeat_type');
            $intervalDailyElement = $('#' + settings['prefix'] + 'interval_daily');
            $intervalWeeklyElement = $('#' + settings['prefix'] + 'interval_weekly');
            $repeatWeeklyDayElement = $('#' + settings['prefix'] + 'repeat_weeklyday');
            $intervalMonthlyElement = $('#' + settings['prefix'] + 'interval_monthly');
            $repeatMonthlyDayElement = $('#' + settings['prefix'] + 'repeat_monthlyday');
            $repeatMonthlyDateElement = $('#' + settings['prefix'] + 'repeat_monthlydate');
            $intervalYearlyElement = $('#' + settings['prefix'] + 'interval_yearly');
            $repeatYearlyMonthElement = $('#' + settings['prefix'] + 'repeat_yearly_month');
            $freqTypeElement = $('#' + settings['prefix'] + 'freq_type');
            $freqCountElement = $('#' + settings['prefix'] + 'freq_count');

            hideAllRuleFieldSets();
            showRuleFieldSets($repeatTypeElement.val());
            hideAllFreqTypeFieldSets();
            buildRule();

            $repeatTypeElement.change(function (e) {
                var $element = $(e.target);

                hideAllRuleFieldSets();
                showRuleFieldSets($element.val());
                buildRule();
            });
            $intervalDailyElement.change(function (e) {
                buildRule();
            });
            $intervalWeeklyElement.change(function (e) {
                buildRule();
            });
            $repeatWeeklyDayElement.change(function (e) {
                buildRule();
            });
            $intervalMonthlyElement.change(function (e) {
                buildRule();
            });
            $repeatMonthlyDayElement.change(function (e) {
                buildRule();
            });
            $repeatMonthlyDateElement.change(function (e) {
                buildRule();
            });
            $intervalYearlyElement.change(function (e) {
                buildRule();
            });
            $repeatYearlyMonthElement.change(function (e) {
                buildRule();
            });
            $freqTypeElement.change(function (e) {
                var $element = $(e.target);

                hideAllFreqTypeFieldSets();
                showFreqTypeFieldSets($element.val());
                buildRule();
            });
            $freqCountElement.change(function (e) {
                buildRule();
            });
        },
        destroy: function () {
            return this.each(function () {
                $(window).unbind('.rrule');
            })
        },
    };

    function hideAllRuleFieldSets() {
        $('.formFieldset.rule').hide();
    }

    function showRuleFieldSets(class_name) {
        $('.formFieldset.rule.' + class_name).show();
    }

    function hideAllFreqTypeFieldSets() {
        $('.formFieldset.freq').hide();
    }

    function showFreqTypeFieldSets(class_name) {
        $('.formFieldset.freq.' + class_name).show();
    }

    function buildRule() {
        var rrule = "",
            dow = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"],
            today = new Date().toISOString().split("T")[0],
            date = splitDate(today);
        
        var intervalDailyValue = $intervalDailyElement.val(),
            intervalWeeklyValue = $intervalWeeklyElement.val(),
            repeatWeeklyDayValue = $repeatWeeklyDayElement.val() || [],
            intervalMonthlyValue = $intervalMonthlyElement.val(),
            repeatMonthlyDayValue = $repeatMonthlyDayElement.val() || [],
            repeatMonthlyDateValue = $repeatMonthlyDateElement.val() || [],
            intervalYearlyValue = $intervalYearlyElement.val(),
            repeatYearlyMonthValue = $repeatYearlyMonthElement.val();

        if (repeatWeeklyDayValue.length == 0) {
            var d = new Date(date[0], date[1] - 1, date[2]);
            var i = d.getDay();
            $repeatWeeklyDayElement.val([dow[i].toUpperCase(),]);
        }
        if (repeatMonthlyDayValue.length == 0) {
            var d = new Date(date[0], date[1] - 1, date[2]);
            var i = d.getDay();
            var week = Math.floor((date[2] - 1) / 7) + 1;
            $repeatMonthlyDayElement.val([week + dow[i].toUpperCase(),]);
        }
        if (repeatMonthlyDateValue.length == 0) {
            $repeatMonthlyDateElement.val([date[2],]);
        }
        if (!intervalYearlyValue) {
            $intervalYearlyElement.val(date[1]);
        }

        switch ($repeatTypeElement.val()) {
            case "d":
                rrule = "FREQ=DAILY;INTERVAL=" + intervalDailyValue;
                break;
            case "w":
                rrule = "FREQ=WEEKLY;INTERVAL=" + intervalWeeklyValue + ";BYDAY=" + repeatWeeklyDayValue.join(',');
                break;
            case "mdate":
                rrule = "FREQ=MONTHLY;INTERVAL=" + intervalMonthlyValue + ";BYMONTHDAY=" + repeatMonthlyDateValue.join(',');
                break;
            case "mday":
                rrule = "FREQ=MONTHLY;INTERVAL=" + intervalMonthlyValue + ";BYDAY=" + repeatMonthlyDayValue.join(',');
                break;
            case "ydate":
                rrule = "FREQ=YEARLY;INTERVAL=" + intervalYearlyValue + ";BYMONTH=" + repeatYearlyMonthValue + ";BYMONTHDAY=" + repeatMonthlyDateValue.join(',');
                break;
            case "yday":
                rrule = "FREQ=YEARLY;INTERVAL=" + intervalYearlyValue + ";BYMONTH=" + repeatYearlyMonthValue + ";BYDAY=" + repeatMonthlyDayValue.join(',');
                break;
        }

        var freqTypeValue = $freqTypeElement.find(':checked').val(),
            freqCountValue = $freqCountElement.val();
        switch (freqTypeValue) {
            case "c":
                if (parseInt(freqCountValue) > 0) {
                    rrule += ";COUNT=" + freqCountValue;
                }
                break;
        }
        $rruleElement.val(rrule);
    }

    function splitDate(date) {
        darray = new Array(); //0-year,1-month,2-day
        if (date.substr(2, 1) == "/") {
            darray[1] = date.substr(0, 2);
            darray[2] = date.substr(3, 2);
            darray[0] = date.substr(6, 4);
        }
        else if (date.substr(2, 1) == ".") {
            darray[2] = date.substr(0, 2);
            darray[1] = date.substr(3, 2);
            darray[0] = date.substr(6, 4);
        }
        else {
            darray[0] = date.substr(0, 4);
            darray[1] = date.substr(5, 2);
            darray[2] = date.substr(8, 2);
        }
        return darray;
    }	

    $.fn.rrule = function (method) {

        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Метод с именем ' + method + ' не существует для jQuery.rrule');
        }

    };
})(jQuery);