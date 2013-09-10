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

$(document).ready(function(){
    $("#alertbox").hide();
});

$("#add_server").click(function(e){
	e.preventDefault();

	var host = $("#host").val();
	var ipv4 = $("#ipv4").val();
	var ipv6 = $("#ipv6").val();

	var post = true;
	
	if((host == "" || !check_vals(host, "h")) && !$("#host").hasClass("alert_border")){
		$("#host").addClass("alert_border");

		post = false;
	} else if((host != "" && check_vals(host, "h")) && $("#host").hasClass("alert_border")){
		$("#host").removeClass("alert_border");
	}

	if((ipv4 == "" || !check_vals(ipv4, "4")) && ipv6 == ""){
		if(!$("#ipv4").hasClass("alert_border")){
			$("#ipv4").addClass("alert_border");
		}

		if(!$("#ipv6").hasClass("alert_border")){
			$("#ipv6").addClass("alert_border");
		}

		post = false;
	} else if(ipv4 == "" && (ipv6 != "" && check_vals(ipv6, "6"))){
		if($("#ipv6").hasClass("alert_border")){
			$("#ipv6").removeClass("#alert_border");
		}
		
		$("#ipv6noipv4").modal("show");
	}
	
	if(!post){
		return false;
	} else{
		$.post("/server/add",
			{host : host, ipv4 : ipv4, ipv6 : ipv6 },
			function(data){
	            var n = data.split("|");
	            var type = n[0];
	            var title = n[1];
	            var msg = n[2];

	            $("#alertbox").show();

	            if(type == "e"){
	            	$("#alertbox").addClass("alert-error");
	            } else{
	            	$("#alertbox").addClass("alert-success");
	            	$("input:text").val("");
	            	$(".alert_border").removeClass("alert_border");
	            }

	            $("#title").html(title);
	            $("#msg").html(msg);
		});
	}
});