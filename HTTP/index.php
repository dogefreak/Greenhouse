<?php
	#Include config
	include 'config.php';
	
	#Get contents from API and decode
	$json = file_get_contents("https://onlinedb.net/".$apikey."/get?fields=id,received,".$temperaturefield.",".$humidityfield."&where=id>0&count=999999999999999999999999999999999999999999999999999999999", 0, stream_context_create(["http"=>["timeout"=>3]]));
	
	if($json !== false AND !empty($json)) {
		$array = json_decode($json);
	
		#Store JSON data in multiple arrays
		foreach ($array as $value) {
			$id[]=$value->id;
			$received[]=$value->received;
			$temp[]=$value->$temperaturefield;
			$hum[]=$value->$humidityfield;
		}
		
		#Timezone correction
		foreach ($received as &$value){
			$date = new DateTime($value);
			$date->modify("+{$timezone_offset} hours");
			$value = $date->format('d/m/Y - H:i');		
		}
		
		#Reverse arrays because of API displaying most recent item first
		$rev_id = array_reverse($id);
		$rev_received = array_reverse($received);
		$rev_temp = array_reverse($temp);
		$rev_hum = array_reverse($hum);
		
		#Remove first items from all arrays because of timezone corretion bug
		array_shift($rev_id);
		array_shift($rev_received);
		array_shift($rev_temp);
		array_shift($rev_hum);
		
		#Remove useless/null results
		foreach ($rev_temp as $key => $value) {
	    	#echo $value . " in " . $key . ", ";
	    	if($value == 0){
		    	unset($rev_id[$key]);
		    	unset($rev_received[$key]);
		    	unset($rev_temp[$key]);
		    	unset($rev_hum[$key]);
	    	}
		}
		
		#Cap daily/weekly data at config defined items
		$w_id = array_slice($rev_id, $resultcap * -1);
		$w_received = array_slice($rev_received, $resultcap * -1);
		$w_temp = array_slice($rev_temp, $resultcap * -1);
		$w_hum = array_slice($rev_hum, $resultcap * -1);

	} else {
		header("Location: /error");
		exit();
	}
?>

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Auto Greenhouse</title>

    <meta name="description" content="2021, Heije F.">
    <meta name="author" content="Heije F.">

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.bundle.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
    <script src="https://npmcdn.com/tether@1.2.4/dist/js/tether.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js"></script>

  </head>
  <body>

    <div class="container-fluid">
	<div class="row">
		<div class="col-md-12">
			<lt class="lt--mac-os text-center text-success">
				<lt class="lt-highlighter__wrapper">
					<lt class="lt-highlighter__scrollElement">
					</lt>
				</lt>
			</lt>
			<p class="lead text-center">
			</p>
			<h3 class="text-center">
				<a class="text-success" href="index"> Auto Greenhouse </a>
			</h3>
			<lt class="lt--mac-os lead text-center">
				<lt class="lt-highlighter__wrapper">
					<lt class="lt-highlighter__scrollElement">
					</lt>
				</lt>
			</lt>
			<p class="lead text-center">
				Welcome to a small insight in our automated greenhouse! Feel free to take a look at the data.
			</p>
		</div>
	</div>
	<div class="row">
		<div class="col-md-6">
			<h6 class="text-center">
				<a href="daily"> Daily Data </a>
			</h6>
			<div style="width: 95%; height: 75vh;  margin-right: auto; margin-left: auto;"> 
			            <canvas id="canvas1"></canvas>
			        </div>
			        <script>
			            var data1 = <?php echo json_encode(array_values($w_id)); ?>;
			            var received1 = <?php echo json_encode(array_values($w_received)); ?>;
			            var temp1 = <?php echo json_encode(array_values($w_temp)); ?>;
			            var hum1 = <?php echo json_encode(array_values($w_hum)); ?>;
						
			            var config1 = {
			                type: 'line',
			                data: {
			                    labels: received1,
			                    datasets: [{
			                        label: "Temperature",
			                        data: temp1,
			                        fill: false
			                    },
			                    {
			                        label: "Humidity",
			                        data: hum1,
			                        fill: false
			                    }]
			                },
			                options: {
			                    responsive: true,
			                    maintainAspectRatio: false,
/*
			                    title:{
			                        display:true,
			                        text:'Weekly Data'
			                    },
*/
			                    tooltips: {
			                        mode: 'label'
			                    },
			                    hover: {
			                        mode: 'dataset'
			                    },
			                    scales: {
			                        xAxes: [{
			                            display: true,
			                            scaleLabel: {
			                                display: true,
			                                labelString: 'Date & Time'
			                            }
			                        }],
			                        yAxes: [{
			                            display: true,
			                            scaleLabel: {
			                                display: true,
			                                labelString: 'Value'
			                            },
			                            ticks: {
			                                suggestedMin: -20,
			                                suggestedMax: 100,
			                            }
			                        }],
			                    }
			                }
			            };
			            
			            var randomScalingFactor = function() {
			                return Math.round(Math.random() * 100);
			            };
			            var randomColorFactor = function() {
			                return Math.round(Math.random() * 255);
			            };
			            var randomColor = function(opacity) {
			                return 'rgba(' + randomColorFactor() + ',' + randomColorFactor() + ',' + randomColorFactor() + ',' + (opacity || '.9') + ')';
			            };
			
			            $.each(config1.data.datasets, function(i, dataset) {
			                dataset.borderColor = randomColor(1.0);
			                dataset.backgroundColor = randomColor(1.0);
			                dataset.pointBorderColor = randomColor(1.0);
			                dataset.pointBackgroundColor = randomColor(1.0);
			                dataset.pointBorderWidth = 1;
			            });
		
			            window.onload = function() {
				           	var ctx1 = document.getElementById("canvas1").getContext("2d");
			                window.myLine = new Chart(ctx1, config1);
			                var ctx2 = document.getElementById("canvas2").getContext("2d");
			                window.myLine = new Chart(ctx2, config2);
			            };
			        </script>
		</div>
		<div class="col-md-6">
			<h6 class="text-center">
				<a href="all"> All Data </a>
			</h6>
			<div style="width: 95%; height: 75vh;  margin-right: auto; margin-left: auto;"> 
			    <canvas id="canvas2"></canvas>
			</div>
			        <script>
			            var data2 = <?php echo json_encode(array_values($rev_id)); ?>;
			            var received2 = <?php echo json_encode(array_values($rev_received)); ?>;
			            var temp2 = <?php echo json_encode(array_values($rev_temp)); ?>;
			            var hum2 = <?php echo json_encode(array_values($rev_hum)); ?>;
						
			            var config2 = {
			                type: 'line',
			                data: {
			                    labels: received2,
			                    datasets: [{
			                        label: "Temperature",
			                        data: temp2,
			                        fill: false
			                    },
			                    {
			                        label: "Humidity",
			                        data: hum2,
			                        fill: false
			                    }]
			                },
			                options: {
			                    responsive: true,
			                    maintainAspectRatio: false,
/*
			                    title:{
			                        display:true,
			                        text:'All Data'
			                    },
*/
			                    tooltips: {
			                        mode: 'label'
			                    },
			                    hover: {
			                        mode: 'dataset'
			                    },
			                    scales: {
			                        xAxes: [{
			                            display: true,
			                            scaleLabel: {
			                                display: true,
			                                labelString: 'Date & Time'
			                            }
			                        }],
			                        yAxes: [{
			                            display: true,
			                            scaleLabel: {
			                                display: true,
			                                labelString: 'Value'
			                            },
			                            ticks: {
			                                suggestedMin: -20,
			                                suggestedMax: 100,
			                            }
			                        }],
			                    }
			                }
			            };
			            
			            var randomScalingFactor = function() {
			                return Math.round(Math.random() * 100);
			            };
			            var randomColorFactor = function() {
			                return Math.round(Math.random() * 255);
			            };
			            var randomColor = function(opacity) {
			                return 'rgba(' + randomColorFactor() + ',' + randomColorFactor() + ',' + randomColorFactor() + ',' + (opacity || '.9') + ')';
			            };
			
			            $.each(config2.data.datasets, function(i, dataset) {
			                dataset.borderColor = randomColor(1.0);
			                dataset.backgroundColor = randomColor(1.0);
			                dataset.pointBorderColor = randomColor(1.0);
			                dataset.pointBackgroundColor = randomColor(1.0);
			                dataset.pointBorderWidth = 1;
			            });
		
			            window.onload = function() {
				           	var ctx1 = document.getElementById("canvas1").getContext("2d");
			                window.myLine = new Chart(ctx1, config1);
			                var ctx2 = document.getElementById("canvas2").getContext("2d");
			                window.myLine = new Chart(ctx2, config2);
			                
			            };
			        </script>
		</div>
	</div>
</div>
  </body>
</html>