$(document).ready(function(){
    $(".alert").hide();
});

$("#genc").click(function(e){
    e.preventDefault();

    $.post("/api",
        {api_act : "genc"},
        function(data){
            var d = data.split("|");

            var title = "";

            $("#add_api_key_msgdiv").show();

            if(d[0] == "s"){
                title = "Challenge generated!";
                $("#add_api_key_msgdiv").removeClass();
                $("#add_api_key_msgdiv").addClass("alert alert-success");
                $("#add_key_submsg").text("Past the following argument to the daemon to complete the process.");
                $("#add_key_msg").val($("#api_ref").text() + "," + d[1]);
            } else{
                $("#add_api_key_msgdiv").removeClass();
                $("#add_api_key_msgdiv").addClass("alert alert-error");
                title = "Unable to generate challenge!";
                $("#add_key_msg").val(d[1]);
            }

            $("#add_key_title").html(title);

            if(d[0] == "s"){
                $("#add_key_msg").select();
            }
        }
    );
});

$("#api_key_add_dialog").on("show", function(){
    $("#add_api_key_msgdiv").hide();
    $("#add_key_msg").val("");
});

$("#api_key_delete").on("show", function(){
    $("#delete_api_key_msgbox").hide();
    $("#dak_msg").html("");

    if($("#conf_delete").hasClass("disabled")){
        $("#conf_delete").removeClass("disabled");
    }
});

$(".api_key_delete").click(function(e){
    e.preventDefault();

    var id = $(this).val();
    var modal = $("#api_key_delete");
    var name = $("#api_server_"+id).val();
    var sid = $("#api_server_"+id+"_sid").val();
    var tid = $(this).closest("tr").attr("id");

    $("#api_key_delete_server").html(name);
    $("#conf_delete").val(sid+"|"+id+"|"+tid);

    modal.modal("show");
});

$("#conf_delete").click(function(e){
    e.preventDefault();

    if($(this).hasClass("disabled")){
        return false;
    }

    var conf = $("#conf_delete").val();
    conf = conf.split("|");

    var server = conf[0];
    var kid = conf[1];
    var tid = conf[2].substring(4);

    $.post("/api",
        {server : server, id : kid, api_act : "deletek"},
        function(data){
            var n = data.split("|");
            var type = n[0];
            var msg = n[1];
            var dak = $("#delete_api_key_msgbox");

            dak.show();

            if(type == "e"){
                dak.addClass("alert-error");
            } else{
                dak.addClass("alert-success");

                $("#conf_delete").addClass("disabled");

                $("#api_key_delete").modal("hide");
                
                var tr = $("#api_server_"+kid).closest("tr");

                tr.fadeOut(400, function(){
                    tr.remove();
                });
            }

            $("#dak_msg").html(msg);
        }
    );
});

$("#key_add_close").click(function(e){
    e.preventDefault();
    window.location = window.location.pathname;
});
