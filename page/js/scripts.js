$(document).ready(function () {
    $('#example_fpgaol2').click(function () {
        $('#inputJobId').val(Math.round(Math.random() * 8388607 + 8388608).toString(16));
        $('#inputXdcFile').text(exampleled[0]);
        $('#inputSrcFile1').text(exampleled[1]);
    });
	//updater.poll();
	$('#submitbutton').click(function () {updater.submit()});
	$('#downloadbutton').click(function (e) {updater.download(e)});
});

//$('#XdcFileName').val("fpgaol01.xdc");
//$('#SrcFileName1').val("top.v");

var updater = {
	sleeptime: 10000,
	ispolling: false,
	polllaunched: false,

	poll: function() {
		if (updater.ispolling) {
			var jobid = $('#inputJobId').val();
			$.ajax({
				url: '/status/' + jobid,
				type: 'GET',
				success: updater.onSuccess,
				error: updater.onError
			});
		} else {
			window.setTimeout(updater.poll, updater.sleeptime);
		}
	},

	onSuccess: function(response) {
		console.log(response);
		if (response == 'finished') {
			console.log("Done!");
			$('#downloadbutton').prop('disabled', false)
			updater.ispolling = false;
		}
		updater.onError(response);
	},

	onError: function(response) {
		$('#server_reply').text(response);
		window.setTimeout(updater.poll, updater.sleeptime);
	},

	submit: function() {
		// here has a timing hazard: should do the post HERE and wait for finish
		// before ispolling = true
		if (!updater.polllaunched) {
			updater.polllaunched = true;
			// this is the first launch of poll
			window.setTimeout(updater.poll, updater.sleeptime);
		}
		updater.ispolling = true;
		$('#downloadbutton').prop('disabled', true)
	},

	download: function(e) {
		e.preventDefault();
		var jobid = $('#inputJobId').val();
		window.location.href = "/download/" + jobid;
			//$.ajax({
				//url: '/download/' + jobid,
				//type: 'GET'
			//});
		//updater.isrunning = false;
	}
}

var exampleled = [` # FPGAOL2
set_property -dict {PACKAGE_PIN B8 IOSTANDARD LVCMOS33} [get_ports {clk}];

set_property -dict {PACKAGE_PIN K17 IOSTANDARD LVCMOS33} [get_ports {led[0]}];
set_property -dict {PACKAGE_PIN K18 IOSTANDARD LVCMOS33} [get_ports {led[1]}];
set_property -dict {PACKAGE_PIN L14 IOSTANDARD LVCMOS33} [get_ports {led[2]}];
set_property -dict {PACKAGE_PIN M14 IOSTANDARD LVCMOS33} [get_ports {led[3]}];
set_property -dict {PACKAGE_PIN L18 IOSTANDARD LVCMOS33} [get_ports {led[4]}];
set_property -dict {PACKAGE_PIN M18 IOSTANDARD LVCMOS33} [get_ports {led[5]}];
set_property -dict {PACKAGE_PIN R12 IOSTANDARD LVCMOS33} [get_ports {led[6]}];
set_property -dict {PACKAGE_PIN R13 IOSTANDARD LVCMOS33} [get_ports {led[7]}];

set_property -dict {PACKAGE_PIN M13 IOSTANDARD LVCMOS33} [get_ports {sw[0]}];
set_property -dict {PACKAGE_PIN R18 IOSTANDARD LVCMOS33} [get_ports {sw[1]}];
set_property -dict {PACKAGE_PIN T18 IOSTANDARD LVCMOS33} [get_ports {sw[2]}];
set_property -dict {PACKAGE_PIN N14 IOSTANDARD LVCMOS33} [get_ports {sw[3]}];
set_property -dict {PACKAGE_PIN P14 IOSTANDARD LVCMOS33} [get_ports {sw[4]}];
set_property -dict {PACKAGE_PIN P18 IOSTANDARD LVCMOS33} [get_ports {sw[5]}];
set_property -dict {PACKAGE_PIN U12 IOSTANDARD LVCMOS33} [get_ports {sw[6]}];
set_property -dict {PACKAGE_PIN U11 IOSTANDARD LVCMOS33} [get_ports {sw[7]}];

set_property -dict {PACKAGE_PIN M16 IOSTANDARD LVCMOS33} [get_ports {uart_rx0}];
set_property -dict {PACKAGE_PIN M17 IOSTANDARD LVCMOS33} [get_ports {uart_tx0}];

set_property -dict {PACKAGE_PIN V14 IOSTANDARD LVCMOS33} [get_ports {hexplay0_an[0]}];
set_property -dict {PACKAGE_PIN U14 IOSTANDARD LVCMOS33} [get_ports {hexplay0_an[1]}];
set_property -dict {PACKAGE_PIN V11 IOSTANDARD LVCMOS33} [get_ports {hexplay0_an[2]}];
set_property -dict {PACKAGE_PIN T10 IOSTANDARD LVCMOS33} [get_ports {hexplay0_d[0]}];
set_property -dict {PACKAGE_PIN T9 IOSTANDARD LVCMOS33} [get_ports {hexplay0_d[1]}];
set_property -dict {PACKAGE_PIN U13 IOSTANDARD LVCMOS33} [get_ports {hexplay0_d[2]}];
set_property -dict {PACKAGE_PIN T13 IOSTANDARD LVCMOS33} [get_ports {hexplay0_d[3]}];
        `,
    `\`timescale 1ns / 1ps
        module top(
            input clk,
            input [7:0] sw,
            output [7:0] led,
            output reg uart_tx0 = 0,
            input uart_rx0,
            output reg [2:0]hexplay0_an = 0,
            output reg [3:0]hexplay0_d = 0
            );
        assign led = ~sw;
	endmodule
        `];
