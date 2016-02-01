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

$("#sendButton").click(function() {
    $("#sendButton").html("Sending ...");
    var data = new FormData();
    data.append("subject", $("#emailSubject").val());
    data.append("body", tinyMCE.activeEditor.getContent());
    data.append("list", $("#selectList").val());

    var files = $("#chooser")[0].files;
    for(var i = 0; i < files.length; i++) {
        var file_name = files[i].name;
        data.append(file_name, files[i], file_name);
    }

    $.ajax({
        type:"POST",
        url:"/send/",
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(data){
            $("#sendButton").html("Send");
            $("#status").show();
            if(data == "true") {
                $("#status").html('<div class="alert alert-success"><strong><i class="fa fa-check"></i></strong> Email has been sent!</div>');
            }
            else {
                $("#status").html('<div class="alert alert-danger"><strong><i class="fa fa-times"></i></strong> Please fill out all fields.</div>');
            }
            setTimeout(function() {
                $("#status").hide();
            }, 5000);                
        }
    });
});