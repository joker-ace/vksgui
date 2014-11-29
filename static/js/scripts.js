// global constants
var timer = null;
var doneTypingInterval = 1000;
var countryId = 0;
var cityId = 0;

// possible cities request processing flag
pcrp = false;

$(document).ready(function () {
    // countries list changed handler
    $("#country").change(function () {
        countryId = parseInt($(this).val());
        if (countryId == 0) {
            $('#city').empty();
            return;
        }
        $.post(
            'getvkcities/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                country: countryId
            },
            function (data) {
                if (data.length == 0) return;
                var lst = $('#city');
                lst.empty();

                data.forEach(function (element, index, array) {
                    if (!element.hasOwnProperty("id")) {
                        return;
                    }
                    if (!element.hasOwnProperty("title")) {
                        return;
                    }

                    lst.append($("<option />")
                        .attr("value", element['id'])
                        .text(element['title']));

                });
                lst.append($("<option />").attr("value", "-1").text("Другой"));
            }
        );
    });

    // cities list changed handler
    $("#city").change(function () {
        cityId = parseInt($(this).val());
        if (cityId == -1) {
            $(this).hide();

            if ($('#city_custom').length) {
                $('#city_custom').show();
                $("#btn-clear").show();
            }
            else {
                var parent = $(this).parent();
                parent.append($('<input />', {
                    'type': 'text',
                    'name': 'city',
                    'id': 'city_custom',
                    'placeholder': 'Другой город'
                }));

                parent.append($('<span>', {
                    'id': 'btn-clear'
                }));

                $("#btn-clear").append($('<img />', {
                    'src': '/static/img/close_btn.png',
                    'alt': 'clear city text'
                })).click(function () {
                    $("#btn-clear").hide();
                    $('#city_custom').hide();
                    var lst = $("#city");
                    lst.show();
                    lst.find('option:first').prop('selected', 'selected');
                });

                $('#city_custom').keyup(cityKeyUp).keydown(cityKeyDown);
            }
        }
    });

});


function cityKeyDown() {
    clearTimeout(timer);
}

function cityKeyUp() {
    if ($(this).val().length < 3) {
        return;
    }
    clearTimeout(timer);
    timer = setTimeout(getPossibleCities, doneTypingInterval);
}


function getPossibleCities() {
    if (pcrp) return;
    pcrp = true;
    var query = $("#city_custom").val() || $('#city').val();
    if (query === '') return;
    $.post(
        'getvkcities/',
        {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            country: countryId,
            query: query
        },

        function (data) {
            var props = ['title', 'area', 'region'];

            var outerDiv = $('#cities-list');
            if (outerDiv.length) {
                outerDiv.html('');
            }
            else {
                outerDiv = $('<div>', {
                    'id': 'cities-list'
                });
            }

            data.forEach(function (city, index, array) {

                var innerDiv = $('<div>', {
                    'class': 'city-row'
                });

                innerDiv.append($('<span>', {
                    'text': city['id']
                }).hide());

                props.forEach(function(property, index, array) {
                   if (city.hasOwnProperty(property)){
                       innerDiv.append(
                           $('<div>', {
                               'class': property,
                               'text': city[property]
                           })
                       );
                   }

                });
                outerDiv.append(innerDiv);
            });
            $("#city").parent().append(outerDiv);

            $(".city-row").click(function(){
                $("#city_custom").val($(this).find(".title").text());
                cityId = parseInt($(this).find("span").text());
                outerDiv.html('');
            });
        }
    );
    pcrp = false;
}