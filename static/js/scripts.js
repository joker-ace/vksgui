$(document).ready(function () {

    // countries list changed handler
    $("#country").change(function () {
        var countryId = parseInt($(this).val());

        $.post(
            'get_cities/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                country: countryId
            },
            function (data) {
                if (data.length == 0) return;
                var lst = $('#city');
                var ID = 0;
                var NAME = 1;
                lst.empty();

                $.each(data, function (index, city) {
                    lst.append($("<option />")
                        .attr("value", city[ID])
                        .text(city[NAME]));
                });
                lst.append($("<option />").attr("value", "-1").text("Другой"));
            }
        );

    });

    // cities list changed handler
    $("#city").change(function () {
        var cityId = parseInt($(this).val());
        if (cityId == -1) {
            $(this).replaceWith($('<input />', {
                'type': 'text',
                'name': 'city',
                'placeholder': 'Другой город'
            }));
        }

        /*
        $.post(
            'get_cities/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                country: countryId
            },
            function (data) {
                if (data.length == 0) return;
                var lst = $('#city');
                var ID = 0;
                var NAME = 1;
                lst.empty();

                $.each(data, function (index, city) {
                    lst.append($("<option />")
                        .attr("value", city[ID])
                        .text(city[NAME]));
                });
                lst.append($("<option />").attr("value", "-1").text("Другой"));
            }
        );*/

    });

});