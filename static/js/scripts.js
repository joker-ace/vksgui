// global constants

var app = {
    timer: 0,
    doneTypingInterval: 1000,
    countryId: null,
    cityId: null,
    groupId: 0,
    taskId: 0,
    parsedFriends: 0,
    requests: {
        cities: false,
        countries: false,
        groups: false
    },
    sex: 0,
    ageFrom: null,
    ageTo: null
};

function sendNotifications(ids) {
    $.post(
        'send_notification/',
        {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            ids: ids.toString()
        },
        function (status) {

        }
    );
}

function getAttackResults() {
    $.post(
        'get_attack_results/',
        {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        },
        function (targets) {
            var rb = $("#results-box");

            if (targets.length == 0) {
                rb.append('<p>Не найдено целей для выбраного сообщества</p>');
                return;
            }

            app.targets = targets;
            var div = $('<div>', {
                'id': 'targets'
            });

            targets.forEach(function (t, i) {

                var tb = $('<div>', {
                    'class': 'target-block'
                });

                var tph = $('<div>', {
                    'class': 'target-photo'
                });

                if (t.can_write_private_message) {
                    tph.append(
                        $('<input>', {
                            'type': 'checkbox',
                            'name': 'targets[]',
                            'value': t.id,
                            'class': 'ch-t'
                        })
                    );
                } else {
                    tph.append(
                        $('<div>', {
                            'style': 'color:red',
                            'class': 'ch-t'
                        }).append($('<i>', {'class': 'icon-ban-circle'}))
                    );
                    tb.prop({'title': 'Пользователь запретил отправку личных сообщений'})
                }

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

            rb.append($('<p>', {
                'html': 'Ведущие аккаунты группы <span id="group-name">' + targets[0]['group_name'] + '</span>'
            }).prepend($('<i>', {'class': 'icon-key', 'style': 'color:rgb(14, 149, 12)'}).html('&nbsp;')));

            rb.append($('<button>', {
                'text': "Оповестить выбранных",
                'id': 'send-notification',
                'class': 'square small mgl10'
            }));

            rb.append($('<button>', {
                'text': "Оповестить всех",
                'id': 'send-notification-to-all',
                'class': 'square small mgl10'
            }));

            $("#send-notification-to-all").click(function () {
                var selected = [];
                app.targets.forEach(function (target) {
                    if (target.can_write_private_message == 1) {
                        selected.push(target.id);
                    }
                });
                sendNotifications(selected);
            });

            $("#send-notification").click(function () {
                var selected = [];
                $("input:checkbox:checked").each(function () {
                    selected.push($(this).val());
                });
                sendNotifications(selected);
            });

            rb.append(div);

            $(".ch-t").click(function (e) {
                e.stopPropagation();
            });

            $(".target-block").click(function () {
                var cb = $(this).find($('input'));
                if (!cb.prop('disabled')) {
                    if (cb.prop('checked')) {
                        cb.prop('checked', false);
                    } else {
                        cb.prop('checked', true);
                    }
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
                        $("#img-wait").remove();
                        $("#icon4").prop('class', 'icon-check').css('color', '#0E950C');
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
                rb.append('<p><i id="icon4" class="icon-check-empty"></i>&nbsp&nbspНачалась направленная атака на сообщество. Дождитесь её окончания!</p>');
                rb.append('<img src="/static/img/ajax-loader.gif" alt="" id="img-wait" />')
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
                        $("#icon3").prop('class', 'icon-check').css('color', '#0E950C');
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
                        $("#icon2").prop('class', 'icon-check').css('color', '#0E950C');
                        var rb = $("#results-box");
                        rb.append('<p><i id="icon3" class="icon-check-empty"></i>&nbsp&nbspПоиск дружественных связей между участниками сообщества</p>');
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
                $("#img-wait").remove();
                $("#icon1").prop('class', 'icon-check').css('color', '#0E950C');
                app.groupMembersCount = count;
                rb.append('<p><i id="icon_" class="icon-user"></i>&nbsp&nbspАктивные участники: ' + count + '</p>');
                $("#icon_").css('color', '#0E950C');
                rb.append('<p><i id="icon2" class="icon-check-empty">&nbsp&nbsp</i>Получение друзей участников сообщества</p>');
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

$(document).click(function () {
    var l = $('#list');
    if (l.length) {
        l.remove();
    }
});

$(document).ready(function () {

    var af = $('#age_from');
    var at = $('#age_to');

    at.change(function () {
        app.ageTo = parseInt($(this).val());
    });

    af.change(function () {
        app.ageFrom = parseInt($(this).val());
        at.empty();

        at.append($('<option>', {
            'value': 0,
            'text': '-- До --'
        }));

        for (var i = app.ageFrom; i <= 80; ++i) {
            at.append($('<option>', {
                'value': i,
                'text': 'до ' + i
            }));
        }
    });

    for (var i = 14; i <= 80; ++i) {
        af.append($('<option>', {
            'value': i,
            'text': 'от ' + i
        }));

        at.append($('<option>', {
            'value': i,
            'text': 'до ' + i
        }));
    }

    $(".radio-row").click(function () {
        var div = $(this);
        var i = div.find("i");
        if (i.prop('class') == 'icon-check-empty') {
            $('.radio-row i').prop('class', 'icon-check-empty');
            i.prop('class', 'icon-check');
            app.sex = parseInt(div.prop('id')[1]);
        } else {
            i.prop('class', 'icon-check-empty');
            app.sex = 0;
        }
    });

    $("#start-search-attack").click(function () {
        $.post(
            'run_search_parser/',
            {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                country_id: app.countryId,
                city_id: app.cityId,
                age_from: app.ageFrom,
                age_to: app.ageTo,
                sex: app.sex
            }, function (data) {
                console.log(data);
            }
        );
    });

    $("#start-group-attack").click(function () {
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
                    rb.append('<p><i id="icon1" class="icon-check-empty"></i>&nbsp&nbspПолучение списка участников сообщества</p>');
                    rb.append('<img src="/static/img/ajax-loader.gif" alt="" id="img-wait"/>');
                    return;
                }
                alert('Bad request');
            }
        );
        return false;
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

});

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
            var outerDiv = $('#list');

            if (outerDiv.length) {
                outerDiv.html('');
            }
            else {
                outerDiv = $('<div>', {
                    'id': 'list'
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
                        'src': group['photo_100'],
                        'width': 70,
                        'height': 70
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
                outerDiv.remove();
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
            country: app.countryId,
            query: query
        },

        function (data) {
            var props = ['title', 'area', 'region'];

            var outerDiv = $('#list');
            if (outerDiv.length) {
                outerDiv.html('');
            }
            else {
                outerDiv = $('<div>', {
                    'id': 'list'
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

            $(".city-row").click(function (event) {
                $("#city_custom").val($(this).find(".title").text());
                app.cityId = parseInt($(this).find("span").text());
                outerDiv.remove();
                event.stopPropagation();
            });
        }
    );
    app.requests.cities = false;
}