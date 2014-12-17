// global constants

var app = {
    timer: 0,
    doneTypingInterval: 1000,
    countryId: 0,
    cityId: 0,
    groupId: 0,
    taskId: 0,
    parsedFriends: 0,
    requests: {
        cities: false,
        countries: false,
        groups: false
    }
};

function getAttackResults() {
    $.post(
        'get_attack_results/',
        {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        },
        function (targets) {
            var div = $('<div>', {
                'id': 'targets'
            });

            targets.forEach(function (t) {
                var tb = $('<div>', {
                    'class': 'target-block'
                });

                var tph = $('<div>', {
                    'class': 'target-photo'
                });

                tph.append(
                    $('<input>', {
                        'type': 'checkbox',
                        'name': 'targets[]',
                        'value': t.id,
                        'class': 'ch-t'
                    })
                );

                var tl = $('<a>', {
                    'href': 'https://vk.com/id' + t.id,
                    'target': '_blank'
                });

                var timg = $('<img>', {
                    'alt': 'Image',
                    'src': t['photo_100']
                });

                tl.append(timg);
                tph.append(tl);

                tb.append(tph);

                tb.append($('<div>', {
                    'class': 'target-name'
                }).append(
                    $('<a>', {
                        'href': 'https://vk.com/id' + t.id,
                        'text': t.first_name + ' ' + t.last_name,
                        'target': '_blank'
                    })
                ));
                div.append(tb);
            });

            $("#results-box").append($('<button>', {
                'text': "Оповестить",
                'id': 'send-notification'
            }));

            $("#send-notification").click(function () {
                var selected = [];
                $("input:checkbox:checked").each(function () {
                    selected.push($(this).val());
                });
                console.log(selected);
            });

            $("#results-box").append(div);
            $(".target-block").click(function () {
                var cb = $(this).find($('input'));
                if (cb.prop('checked')) {
                    cb.prop('checked', false);
                } else {
                    cb.prop('checked', true);
                }
            });
        }
    );
}

function runProgressCheckerForAttack() {
    app.intervalId = setInterval(function () {
        $.post(
            'get_attack_status/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            },
            function (status) {
                if (status == -1) {
                    console.log('Error getting attack status!');
                    clearInterval(app.intervalId);
                } else {
                    if (status) {
                        clearInterval(app.intervalId);
                        $("#waiting").remove();
                        $("#results-box").append('<p>Завершенно</p>');
                        getAttackResults();
                    }
                }
            }
        );
    }, 1000);
}

function runPercolationAttack() {
    $.post(
        'run_attack/',
        {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        },
        function (data) {
            if (data == 1) {
                runProgressCheckerForAttack();
                var rb = $("#results-box");
                rb.append('<p>Началась направленная атака на сообщество. Дождитесь её окончания!</p>');
                rb.append('<img src="/static/img/ajax-loader.gif" alt="" id="waiting" />')
            } else {
                console.log('Error!');
            }
        }
    );
}

function updateProgressBar(id, percentage) {
    $("#" + id).css("width", (percentage + "%"));
}

function runProgressCheckerForRelationsSearch() {
    app.intervalId = setInterval(function () {
        $.post(
            'relations_search_status/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            },
            function (data) {
                if (data == -1) {
                    console.log('Error getting count parsed members with relations!');
                    clearInterval(app.intervalId);
                } else {
                    if (data['ready']) {
                        clearInterval(app.intervalId);
                        $("#progressbar").remove();
                        var rb = $("#results-box");
                        rb.append('<p>Завершенно</p>');
                        runPercolationAttack();
                    } else {
                        app.parsedRelations = data['parsed'];
                        updateProgressBar("progress", ((app.parsedRelations / app.groupMembersCount) * 100));
                    }
                }
            }
        );
    }, 1000);
}

function runRelationsSearch() {
    $.post(
        'run_relations_search/',
        {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        },
        function (data) {
            if (data == 1) {
                runProgressCheckerForRelationsSearch();
            } else {
                console.log('Error!');
            }
        }
    );
}

function runProgressCheckerForFriendsParsing() {
    app.intervalId = setInterval(function () {
        $.post(
            'friends_parsing_status/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            },
            function (data) {
                if (data == -1) {
                    console.log('Error getting count of parsed friends!');
                    clearInterval(app.intervalId);
                } else {
                    if (data['ready']) {
                        clearInterval(app.intervalId);
                        $("#progressbar").remove();
                        var rb = $("#results-box");
                        rb.append('<p>Завершенно</p>');
                        rb.append('<p>Поиск дружественных связей между участниками сообщества</p>');
                        rb.append('<div id="progressbar"><div id="progress"></div></div>');
                        runRelationsSearch();
                    } else {
                        app.parsedFriends = data['parsed'];
                        updateProgressBar("progress", ((app.parsedFriends / app.groupMembersCount) * 100));
                    }
                }
            }
        );
    }, 3000);
}


function getGroupMembersCount() {
    $.post(
        'get_group_members_count/',
        {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        },
        function (count) {
            if (count >= 0) {
                var rb = $("#results-box");
                $("#progress").remove();
                app.groupMembersCount = count;
                rb.append('<p>Активные участники: ' + count + '</p>');
                rb.append('<p>Получение друзей участников сообщества</p>');
                rb.append('<div id="progressbar"><div id="progress"></div></div>');
                runProgressCheckerForFriendsParsing();
            } else {
                $("#results-box").html('<p style="color:red">Error!!!</p>');
            }
        }
    );
}

function runProgressCheckerForGroupParsing() {
    app.intervalId = setInterval(function () {
        $.post(
            'group_parsing_status/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            },
            function (status) {
                if (status == -1) {
                    // DEBUG
                    console.log('Error!');
                    clearInterval(app.intervalId);
                } else if (status) {
                    clearInterval(app.intervalId);
                    getGroupMembersCount();
                }
            }
        );
    }, 1000);
}

$(document).ready(function () {

    $("#start").click(function () {
        $.post(
            'run_group_parser/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                gid: $("#group_id").val()
            },
            function (count) {
                if (count >= 0) {
                    runProgressCheckerForGroupParsing();
                    var rb = $("#results-box");
                    rb.html('');
                    rb.append('<p>Получение списка участников сообщества</p>');
                    rb.append('<img src="/static/img/ajax-loader.gif" alt="" id="progress"/>');
                    return;
                }
                alert('Bad request');
            }
        );
    });

    // countries list changed handler
    $("#country").change(function () {
        app.countryId = parseInt($(this).val());
        if (app.countryId == 0) {
            $('#city').empty();
            return;
        }

        $.post(
            'get_cities/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                country: app.countryId
            },
            function (data) {
                if (data.length == 0) return;
                var lst = $('#city');
                lst.empty();

                data.forEach(function (element) {
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
        app.cityId = parseInt($(this).val());
        if (app.cityId == -1) {
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

    $('.sidebar-header').click(function () {
        $('.sidebar-header').removeClass('selected');
        $(this).addClass("selected");

        if ($(this).attr('id') == "groups") {
            $("#groups-filter-form").show();
            $("#common-filter-form").hide();
        } else if ($(this).attr('id') == "common") {
            $("#groups-filter-form").hide();
            $("#common-filter-form").show();
        }
    });

    $('#group_name').keyup(groupKeyUp).keydown(groupKeyDown);

})
;

function groupKeyDown() {
    clearTimeout(app.timer);
}

function groupKeyUp() {
    if ($(this).val().length < 3) {
        return;
    }
    clearTimeout(app.timer);
    app.timer = setTimeout(getGroups, app.doneTypingInterval);
}

function getGroups() {
    if (app.requests.groups) return;
    app.requests.groups = true;
    var query = $("#group_name").val();
    if (query === '') return;
    var type = $("#group_type").val();
    $.post(
        'get_groups/',
        {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            query: query,
            type: type
        },

        function (data) {
            var outerDiv = $('#groups-list');

            if (outerDiv.length) {
                outerDiv.html('');
            }
            else {
                outerDiv = $('<div>', {
                    'id': 'groups-list'
                });
            }

            data.forEach(function (group) {

                var innerDiv = $('<div>', {
                    'class': 'group-row'
                });

                innerDiv.append($('<span>', {
                    'text': group['id']
                }).hide());

                innerDiv.append(
                    $('<img>', {
                        'alt': 'Image',
                        'src': group['photo_50']
                    })
                );

                innerDiv.append(
                    $('<div>', {
                        'class': 'name',
                        'text': group['name']
                    })
                );
                outerDiv.append(innerDiv);
            });
            $("#group_name").parent().append(outerDiv);

            $(".group-row").click(function () {
                $("#group_name").val($(this).find(".name").text());
                app.groupId = parseInt($(this).find("span").text());
                $("#group_id").val($(this).find("span").text());
                outerDiv.html('');
            });
        }
    );
    app.requests.groups = false;
}

function cityKeyDown() {
    clearTimeout(app.timer);
}

function cityKeyUp() {
    if ($(this).val().length < 3) {
        return;
    }
    clearTimeout(app.timer);
    app.timer = setTimeout(getCities, app.doneTypingInterval);
}

function getCities() {
    if (app.requests.cities) return;
    app.requests.cities = true;

    var query = $("#city_custom").val() || $('#city').val();
    if (query === '') return;
    $.post(
        'get_cities/',
        {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            country: app.cityId,
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

            data.forEach(function (city) {

                var innerDiv = $('<div>', {
                    'class': 'city-row'
                });

                innerDiv.append($('<span>', {
                    'text': city['id']
                }).hide());

                props.forEach(function (property) {
                    if (city.hasOwnProperty(property)) {
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

            $(".city-row").click(function () {
                $("#city_custom").val($(this).find(".title").text());
                app.cityId = parseInt($(this).find("span").text());
                outerDiv.html('');
            });
        }
    );
    app.requests.cities = false;
}