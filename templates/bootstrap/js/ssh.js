$(document).ready(function(){
	var srvid = $("#srvid").val();

	var server = "";
	var sport = 0;
	var gport = 0;

	$.post("/ssh/"+srvid,
		{},
		function(data){
			var ret = data.split("|");
			server = ret[0];
			sport = ret[1];
			ghost = ret[2];
			gport = ret[3];
			$("#invalid_data_dialog").modal('hide');

		    var err = "";
		    var msg = "";

		    if(!server){
		        err = "Missing server hostname";
		        msg = "Unable to retrieve server hostname.  Please make sure this server is properly configured.";
		    } else if(gport == 0){
		        err = "Missing GateOne port";
		        msg = "Unable to retrieve GateOne port number.  Make sure GateOne client is installed and set up properly on the server, and that /opt/gateone/settings/ has the server configuration information.";
		    } else if(sport == 0){
		        err = "Missing SSH port";
		        msg = "A valid SSH port must be provided to connect to the server.  Please see the daemon's config file for more information.";
		    }

		    if(!err){
		    	console.log("server:"+server+";go: "+ghost+":"+gport+";sport: "+sport);
		        // Initialize Gate One:
		        GateOne.init({url: 'https://'+ghost+':'+gport+'/',
		            autoConnectURL : 'ssh://'+server+':'+sport, 
		            showTitle : false, showToolbar : false, fillContainer : true});
		    } else{
		        $("#err_why").text(err);
		        $("#err_msg").text(msg);
		        $("#invalid_data_dialog").modal('show');
		    }
		}
	);
});

$("#upload_ssh_keys").click(function(e){
	e.preventDefault();
	GateOne.SSH.uploadIDForm();
});

$("#upload_x509_cert").click(function(e){
	e.preventDefault();
	GateOne.SSH.uploadCertificateForm();
});

$("#manage_ids").click(function(e){
	e.preventDefault();
	GateOne.SSH.loadIDs();
});

$("#back_main").click(function(e){
	e.preventDefault();
	window.location.href = "/";
});