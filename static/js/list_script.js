$(".chip i.fa").click(function() {
    $(this).parent().remove();
});

$(".newEmailInput").keypress(function(e) {
    if(e.which == 13) {
        e.preventDefault();
        addChip($(this));
    }
});

$(".addEmail").click(function() {
    addChip($(this));
});

var addChip = function(el) {
    var chip = createChip(el.parent().find(".newEmailInput").val());
    el.parent().parent().parent().find(".editable").append(chip);
}

var createChip = function(input) {
    return $('<div />', {
        "class": "chip",
        text: input
    }).append($('<i />', {
        "class": 'fa fa-times',
        click: function(e){
            $(this).parent().remove();
        }
    }));
};

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        }
    }
});

$(".save-list").click(function() {
    var thisButton = $(this);
    thisButton.html("Saving ...");
    var chips = $(this).closest(".row").parent().find(".editable .chip");
    var emails = [];
    for(var i = 0; i < chips.length; i++) {
        emails.push($(chips[i]).text().trim());
    }
    $.ajax({
        type:"POST",
        url:"/save-list/",
        dataType: "json",
        data: {
            "list_name": $(this).parent().find("input[name='list_name']").val(),
            "emails": emails
        },
        success: function(data){
            if(data != "200") {
                alert("Something went wrong.");
            }
            thisButton.html("Save");
        }
    });
});

$("#export-list").click(function() {
    $("#export-list").html("Exporting ...");
    $.ajax({
        type:"POST",
        url:"/export-list/",
        dataType: "json",
        data: {
            "list_name": "export"
        },
        success: function(data){
            $("#export-list").html("Export");
            var data = data["data"];
            var result = "";
            for(var i = 0; i < data.length; i++) {
                result += "Street: " + data[i][0] + "\n";
                var emails = data[i][1];
                for(var j = 0; j < emails.length; j++) {
                    result += emails[j] + "\n";
                }
                result += "-------------------------------\n\n";
            }
            var blob = new Blob([result], {type: "text/plain;charset=utf-8"});
            saveAs(blob, "emails.txt");
        }
    }); 
});