var update_status = function(){

	$(".status").each(function(){
		var sid = $(this).attr('alt');
		var ipv4 = $("#server_"+sid+"_ipv4").html();

		$.post("/",
			{action : "update_status", server : sid, ipv4 : ipv4},
			function(data){
				$("#server_"+sid).removeClass().addClass("status icon-"+server_status[data]);
			});
	});
}

setInterval(update_status, 1000*5);