if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}

/**
 * Regex to check values of server information.
 **/
function check_vals(s,t){
    var ipv4reg = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))$/;
    // var ipv6reg = /^((?=.{1,255}$)[0-9A-Za-z](?:(?:[0-9A-Za-z]|\b-){0,61}[0-9A-Za-z])?(?:\.[0-9A-Za-z](?:(?:[0-9A-Za-z]|\b-){0,61}[0-9A-Za-z])?)*\.?)$/;
    var ipv6reg = /^((?=.*::)(?!.*::.+::)(::)?([\dA-F]{1,4}:(:|\b)|){5}|([\dA-F]{1,4}:){6})((([\dA-F]{1,4}((?!\3)::|:\b|$))|(?!\2\3)){2}|(((2[0-4]|1\d|[1-9])?\d|25[0-5])\.?\b){4})$/i;
    var hostreg = /^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$/;

    if(t == "4" && ipv4reg.test(s)){
        return true;
    } else if(t == "6" && ipv6reg.test(s)){
        return true;
    } else if(t == "h" && hostreg.test(s)){
        return true;
    }

    return false;
}

/**
 * Used to generate public key (random text)
 **/
function randString(n)
{
    if(!n)
    {
        n = Math.floor(Math.random() * 16) + 5;
    }

    v = Math.floor(n/2);

    if(v < 1){
    	v = 10;
    }

    var text = '';
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for(var i=0; i < v; i++){
    	text += possible.charAt(Math.floor(Math.random() * possible.length));
    }

    text += "-";

    for(var i=0; i < n; i++)
    {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }

    return text;
}

/**
 * Used to check for status updates of servers.
 **/
var update_status = function(){
	var server_status = ["arrow-down", "arrow-up", "warning-sign"];
	var status_name = ["Down", "Up", "N/A"];

	$(".status").each(function(){
		var sid = $(this).attr('alt');
		var ipv4 = $("#server_"+sid+"_ipv4").html();
		var ipv6 = $("#server_"+sid+"_ipv6").html();

		$.post("/",
			{action : "update_status", server : sid, ipv4 : ipv4, ipv6 : ipv6},
			function(data){
				var title = $("#server_"+sid).attr("title");

				// Only update the tooltip and icon if the status has changed
				if(title != status_name){
					$("#server_"+sid).attr('title', status_name[data]).tooltip('fixTitle');
					$("#server_"+sid).attr('title', status_name[data]);
					$("#server_"+sid).removeClass().addClass("status icon-"+server_status[data]);
				}
			});
	});
}

var check_reports = function(){
    $("tr.server_entry").each(function(){
        var sid = $(this).attr("data-sid");
        
        $.post("/reports",
            {action : "check_report", server : sid},
            function (data){
                var ret = data.split("|");
                var id = "#server_"+ret[0]+"_alert";
        
                if(ret[1] == "1"){
                    if(!$(id).hasClass("icon-exclamation-sign")){
                        $(id).addClass("icon-exclamation-sign");
                    }
                } else{
                    if($(id).hasClass("icon-exclamation-sign")){
                        $(id).removeClass("icon-exclamation-sign");
                    }
                }
            });
    });
}

/**
 * Any unread reports will be flashed so the user is aware of them.
 **/
// setInterval("$('.icon-exclamation-sign').toggle();", 250);

/**
 * Run update_status function every x seconds.
 * Change '5' to # in seconds (so 10 seconds = 1000 * 10).
 **/
setInterval(update_status, 1000*5);

/**
 * Check for new reports every 2 seconds (increment if there are a lot of servers)
 **/
setInterval(check_reports, 1000*2);

/**
 * Deleting a server?  Alright!
 **/
$(".server_delete").click(function(e){
	e.preventDefault();

	var id = $(this).val();
	
	$.post("/",
		{action: "delete_server", server : id},
		function(data){
			console.log("data: "+data);
			if(data == 1){
				var tr = $("#server_"+id+"_row");

                tr.fadeOut(400, function(){
                    tr.remove();
                });
			} else if(data == 2){
                $("#msg_dialog").modal("show");
                $("#msg_dialog").find("#label").html("Error Processing Request");
                $("#msg_dialog_body").html("Unable to locate server "+id+" in API key database.");
            }
		}
	);
});

$(".update").click(function(e){
	e.preventDefault();

	var id = $(this).val();
    
    $("#update_server_dialog").modal("show");
	$("#usd_srv").text($("#server_"+id+"_host").text());
    $("#update_output").html("Once the system's update process has finished a report will be viewable.");
            
	$.post("/",
		{action: "update_server", server : id},
        function (next_run){
            $("#update_output").append("<br /><br />Next run time for cron: "+next_run);
        });
});

$(".cc").click(function(e){
	e.preventDefault();

	var id = $(this).val();
    
    $("#cc_dialog").modal("show");
	$("#ccd_srv").text($("#server_"+id+"_host").text());
    $("#ccd_srv").attr("data-sid", id);
});

$("#perform_cc").click(function(e){
    e.preventDefault();
    var id = $("#ccd_srv").attr("data-sid");
    var cmd = $("#cc_cmd").val();
    console.log(cmd);
    $.post("/",
    {action : "cc", server : id, cmd : cmd},
    function (next_run){
        $("#cc_notice").html("<br /><br />"+cmd+" is set to be processed at "+next_run+".  Once the results are returned a report will be generated and viewable.");
    }
    );
});

$(".shutdown").click(function(e){
	e.preventDefault();
	
	var id = $(this).val();
	
	$.post("/",
		{action : "shutdown_server", server : id},
		function(data){
			$("#shutdown_server_dialog").modal("show");
		}
	);
});

/**
 * Custom command sent across network request...!
 **/
$(".cc_all").click(function(e){
	e.preventDefault();

	$("#action_dialog").modal('show');
	$("#act_label").html("Network Custom Command");
	$("#act_form").append("<input type='text' id='net_cc' value='' />");
	$("#act_foot").append("<button class='btn btn-danger do_cc_all'>Execute Command</button>");
});

$("#action_dialog").on('shown', function(){
	$(".do_cc_all").click(function(e){
		e.preventDefault();
		console.log("CLICKED");
	});
});

/**
 * Since the content is made dynamically we should clear it as well.
 **/
$("#action_dialog").on('hidden', function(){
	$("#act_label").html("");
	$("#act_form").html("");
	$("#act_foot").html("");
});

$(".server_action").click(function(e){
	e.preventDefault();

	var button = $(this);
	var state = button.attr('data-title');
	var id = button.val();
	var tr = $(this).closest('tr');

	if(state == "Edit"){
		tr.find(".editable").each(function(){
			var val = $(this).text();
			$(this).parent().html("<input type='text' class='input_edit' id='input_"+$(this).attr('id')+"' value='"+val+"' />");
		});

		button.attr('title', "Save").tooltip('fixTitle').tooltip('show');
		button.attr('data-title', "Save");
		$("#server_"+id+"_modify").removeClass("icon-edit").addClass("icon-check");
	} else if(state == "Save"){
		var host = "";
		var ipv4 = "";
		var ipv6 = $("input_server_"+id+"_ipv6").val();
		var post = true;

		tr.find(".input_edit").each(function(){
			var val = $(this).val();
			var spanid = $(this).attr('id').substring(6);

			if(spanid.endsWith("host")){
				if((val == "" || !check_vals(val, "h")) && !$(this).hasClass("alert_border")){
					$(this).addClass("alert_border");

					post = false;
				} else if(val != "" && check_vals(val, "h")){
					if($(this).hasClass("alert_border")){
						$(this).removeClass("alert_border");
					}

					host = val;
				}
			} else if(spanid.endsWith("ipv4")){
				if((val == "" || !check_vals(val, "4")) && ipv6 == ""){
					if(!$(this).hasClass("alert_border")){
						$(this).addClass("alert_border");
					}

					if(!$("#input_server_"+id+"_ipv6").hasClass("alert_border")){
						$("#input_server_"+id+"_ipv6").addClass("alert_border");
					}

					post = false;
				} else if(val == "" && (ipv6 != "" && check_vals(ipv6, "6"))){
					if($("#ipv6").hasClass("alert_border")){
						$("#ipv6").removeClass("#alert_border");
					}
				}

				if(post)
					ipv4 = val;
			}
		});

		if(post){
			$.post("/",
				{action : "edit_server", ipv4 : ipv4, ipv6 : ipv6, server : id },
				function(data){
					if(data == 1){
						tr.find(".input_edit").each(function(){
							var val = $(this).val();
							var spanid = $(this).attr('id').substring(6);

							if(spanid.endsWith("_host")){
								$(this).parent().html("<span class=\"editable\" id=\""+spanid+"\"><a href=\"/server/"+id+"\">"+val+"</a></span>");
							} else{
								$(this).parent().html("<span class=\"editable\" id=\""+spanid+"\">"+val+"</span>");
							}
							
							$(this).remove();
						});
						
						button.attr('title', "Edit").tooltip('fixTitle').tooltip('show');
						button.attr("data-title", "Edit");
						$("#server_"+id+"_modify").removeClass("icon-check").addClass("icon-edit");
					}
				}
			);
		}
	}
});

$(".server_entry").on('click', '.icon-exclamation-sign', function(e){
    e.preventDefault();
    
    var sid = $(this).attr('data-sid');
    var dateconv = function(ind){
        var date = new Date(ind * 1000);
        return date.toLocaleString().trim();
    }
    
    $("#reports_dialog_body").html("<div class=\"accordion\" id=\"accordion2\">");
    
    $.post("/reports",
        {action : "fetch_reports", server : sid},
        function (dump){
            dump = JSON.parse(dump);
            var status = ["error", "success", "info"];
            var stat_id = 0;
            
            $.each(dump, function(key, data){
                if(data['status'] > -1 && data['status'] < 3){
                    stat_id = data['status'];
                }
                
                $("#reports_dialog_body").append("<div class=\"accordion-group\"><div class=\"accordion-heading alert-"+status[stat_id]+"\" data-sid=\""+sid+"\" data-rid=\""+data['id']+"\"><a class=\"accordion-toggle\" data-toggle=\"collapse\" data-parent=\"#accordion2\" href=\"#collapse"+data['id']+"\">"+data['title']+"</a></div><div id=\"collapse"+data['id']+"\" class=\"accordion-body collapse\"><div class=\"accordion-inner\"><b>Date</b>&nbsp;&nbsp;"+dateconv(data['ts'])+"<br /><br />"+data['msg'].replace(/\n/g, '<br />')+"</div></div></div>");
            });
        });
    
    $("#reports_dialog_body").append("</div>");
    $("#reports_dialog").modal('show');
});

$("#reports_dialog_body").on('click', '.accordion-heading', function(e){
    var sid = $(this).attr('data-sid');
    var rid = $(this).attr('data-rid');
    
    $.post("/reports",
    {action : "update_report", server : sid, report_id : rid}
    );
});
