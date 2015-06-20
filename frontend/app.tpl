<!DOCTYPE html>
<html lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>LasaurApp</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <!--<link rel="stylesheet" href="/css/bootstrap.min.css" type="text/css">-->
        <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
        <link rel="stylesheet" href="/css/jquery.toastmessage.css" type="text/css">
        <link rel="stylesheet" href="/css/roboto.min.css" type="text/css">
        <link rel="stylesheet" href="/css/material-fullpalette.min.css" type="text/css">
        <link rel="stylesheet" href="/css/ripples.min.css" type="text/css">
        <link rel="stylesheet" href="/css/style.css" type="text/css">

        <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
        <!--[if lt IE 9]>
          <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
          <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
        <![endif]-->
    </head>
    <body>
        <nav class="navbar navbar-fixed-top">
            <div class="container">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                        <span class="sr-only">{{Toggle navigation}}</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="/" style="color:white;line-height: 26px;">
                        <img src="/img/lasersaur-dino-brand.png" style="margin-right:6px; display: inline;">
                        LasaurApp
                    </a>
                </div>

                <div id="navbar" class="collapse navbar-collapse">
                    <a class="btn btn-default navbar-btn" data-toggle="collapse" data-target=".navbar-collapse">
                        <span class="glyphicon glyphicon-bar"></span>
                        <span class="glyphicon glyphicon-bar"></span>
                        <span class="glyphicon glyphicon-bar"></span>
                    </a>
                    <div class="btn-group pull-right">
                        <button id="connect_btn" class="btn btn-default btn-warning" type="submit">Disconnected</button>
                        <button id="door_status_btn" class="btn btn-default disabled btn-warning" type="submit">Door</button>
                        <button id="chiller_status_btn" class="btn btn-default disabled btn-warning" type="submit">Chiller</button>
                    </div>
                    <div class="btn-group pull-right">
                        <button id="go_to_origin" class="btn btn-default " type="submit" title="move to origin">(0,0)</button>
                        <button id="homing_cycle" class="btn btn-default " type="submit" title="run homing cycle, find table origin">
                            <i class="glyphicon glyphicon-home"></i>
                        </button>
                        <button id="cancel_btn" class="btn btn-default " type="submit" title="stop and purge job">
                            <i class="glyphicon glyphicon-stop"></i>
                        </button>
                        <button id="pause_btn" class="btn btn-default pull-right" type="submit" title="pause/continue">
                            <i class="glyphicon glyphicon-pause"></i>
                        </button>
                    </div>

                    <ul class="nav navbar-nav">
                        <li><a href="#about_modal" data-toggle="modal">{{About}}</a></li>

                        <li class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown">Manual<b class="caret"></b></a>
                            <ul class="dropdown-menu">
                                <li><a href="http://www.lasersaur.com/manual/">Manual TOC</a></li>
                                <li><a href="http://www.lasersaur.com/manual/operation">Operating a Lasersaur</a></li>
                                <li><a href="http://www.lasersaur.com/manual/lasertags">LaserTags</a></li>
                            </ul>
                        </li>
                        <li class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown">Admin<b class="caret"></b></a>
                            <ul class="dropdown-menu">
                                <li><a href="flash_firmware">Flash Firmware (latest)</a></li>
                                <li><a href="build_firmware">Build and Flash from Source</a></li>
                                <li><a id="reset_atmega" href="reset_atmega">Reset Atmega (restarts firmware)</a></li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <!-- about modal -->
        <div id="about_modal" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title">About LasersaurApp</h4>
              </div>
              <div class="modal-body">
                <p><img src="/img/lasersaur-black_w530.jpg"></p>
                <div style="width:60px;margin-left:auto;margin-right:auto;margin-top:20px;margin-bottom:20px"><img src="/img/lasersaur-dino.png" style="width:60px"></div>
                <p>LasaurApp is the offical control app for the Lasersaur laser cutter and part of the <a href="http://www.lasersaur.com/">Lasersaur project</a>. This software is made available under the <a href="https://gnu.org/licenses/gpl.html">GPLv3 (version 3 or later)</a> software license. Copyright (c) 2013 <a href="http://labs.nortd.com/">Nortd Labs</a></p>
                <ul>
                    <li>LasaurApp version <span id="lasaurapp_version"></span></li>
                    <li>Firmware version <span id="firmware_version">&lt;not connected&gt;</span></li>
                </ul>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
              </div>
            </div><!-- /.modal-content -->
          </div><!-- /.modal-dialog -->
        </div><!-- /.modal -->

        <!-- cancel modal -->
        <div id="cancel_modal" class="modal fade" tabindex="-1" role="dialog" aria-labelledby="cancel_modal_label" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 id="cancel_modal_label" class="modal-title">Stop Job</h4>
              </div>
              <div class="modal-body">
                <p>Press ENTER to confirm stopping the current job.</p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                <button id="really_cancel_btn" class="btn btn-danger">Stop Job!</button>
              </div>
            </div><!-- /.modal-content -->
          </div><!-- /.modal-dialog -->
        </div><!-- /.modal -->

        <!-- door open warning modal -->
        <div id="door_open_warning_modal" class="modal fade" tabindex="-1" role="dialog" aria-labelledby="door_open_warning_modal_label" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 id="door_open_warning_modal_label" class="modal-title">Door is open</h4>
              </div>
              <div class="modal-body">
                <p>Are you sure you want to start the job with an open Door?</p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-default" data-dismiss="modal">No</button>
                <button id="really_submit_job_btn" class="btn btn-danger">Sure I know what I'm doing</button>
              </div>
            </div><!-- /.modal-content -->
          </div><!-- /.modal-dialog -->
        </div><!-- /.modal -->

        <div id="container" class="container">
            <div class="row">
                <div class="col-md-12">
                    <div class="tabbable row">
                        <!--tabbar start-->
                        <div class="col-md-2">
                            <ul class="nav nav-default nav-pills nav-stacked" role="group">
                                <li class="active">
                                    <a class="btn btn-link" href="#tab_jobs" id="tab_jobs_button" data-toggle="tab" style="text-align: left;">
                                        <i class="glyphicon glyphicon-th-list" style="margin-right:2px"></i>
                                        Laser Jobs
                                    </a>
                                </li>
                                <li>
                                    <a class="btn btn-link " href="#tab_import" id="tab_import_button" data-toggle="tab" style="text-align: left;">
                                        <i class="glyphicon glyphicon-folder-open" style="margin-right:2px"></i>
                                        File Import
                                    </a>
                                </li>
                                <li>
                                    <a class="btn btn-link " href="#tab_mover" id="tab_mover_button" data-toggle="tab" style="text-align: left;">
                                        <i class="glyphicon glyphicon-move" style="margin-right:2px"></i>
                                        Move/Jog
                                    </a>
                                </li>
                                <li>
                                    <a class="btn btn-link " href="#tab_logs" id="tab_logs_button" data-toggle="tab" style="text-align: left;">
                                        <i class="glyphicon glyphicon-exclamation-sign" style="margin-right:2px"></i>
                                        Logs
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <!--tabbar end-->
                        <div class="col-md-10">
                            <div class="tab-content" style="overflow:visible; padding-bottom:30px">
                                <!--content start-->
                                <div id="tab_jobs" class="tab-pane active row">
                                    <div class="col-md-9">
                                        <div class="well clearfix" style="margin-bottom:40px">
                                            <input type="text" id="job_name" style="width:296px;padding-left: 5px;" placeholder="Load or import a job.">
                                            <button id="file_import_quick_btn" class="btn btn-default pull-right" title="file import" data-delay="500" style="margin-top:0;">
                                                <span class="glyphicon glyphicon-folder-open"></span>
                                            </button>
                                            <textarea id="job_data" style="display:none"></textarea>
                                            <div id="preview_canvas_container"></div>
                                            <!-- passes -->
                                            <div id="passes_container" class="clearfix" style="width:594px; margin:0px; margin-top:10px; padding:15px; background-color:#dddddd; display:none">
                                                <div id="passes_info" class="pull-right" style="width:180px; color:#888888; display:none">
                                                    <p>Vector cuts: Use one or more passes with different cut parameters (feedrate, intensity). Assign path colors to passes as needed.</p>
                                                    <p>Need <a id="add_pass_btn" href="">more passes?</a></p>
                                                </div>
                                                <div id="passes" class="pull-left" style="width:350px">
                                                    <!-- passes go here -->
                                                </div>
                                            </div>
                                            <div style="padding-top:20px">
                                                <div class="btn-group pull-left">
                                                    <button id="job_submit" class="btn btn-lg btn-primary">Send to Lasersaur</button>
                                                    <button id="job_bbox_submit" class="btn btn-lg btn-primary" title="send bounding box to lasersaur" data-delay="500">
                                                    <span class="glyphicon glyphicon-resize-full glyphicon glyphicon-white"></span>
                                                    </button>
                                                </div>
                                                <div id="stats_after_name" class="pull-left" style="margin-left:20px;padding-top:23px;color:#888888"></div>
                                                <div class="btn-group pull-right">
                                                    <a class="btn btn-default btn-lg dropdown-toggle" data-toggle="dropdown" href="#">
                                                        <span class="glyphicon glyphicon-share-alt"></span>
                                                        <span class="caret"></span>
                                                    </a>
                                                    <ul class="dropdown-menu">
                                                        <li><a id="export_json_btn" href="#">Export Job as JSON</a></li>
                                                        <li><a id="export_gcode_btn" href="#">Export Job as G-Code</a></li>
                                                    </ul>
                                                </div>
                                                <button id="job_save_to_queue" class="btn btn-default btn-lg pull-right" title="add to queue" data-delay="500" style="margin-right:10px">
                                                <span class="glyphicon glyphicon-th-list"></span>
                                                </button>
                                            </div>
                                            <div id="progressbar" class="progress progress-striped" style="margin-top:70px; clear:both">
                                                <div class="progress-bar" style="width:0%;"></div>
                                            </div>
                                        </div>
                                        <button id="clear_queue" class="btn btn-default btn-xs pull-right" title="delete non-starred jobs" data-delay="500">
                                            clear
                                        </button>
                                        <h3>Recent Jobs</h3>
                                        <div>
                                            <ul id="job_queue" class="nav nav-pills nav-stacked">
                                                <!-- job queue -->
                                            </ul>
                                            <div class="btn-group dropup">
                                                <a class="btn btn-default btn-lg dropdown-toggle" data-toggle="dropdown" href="#">
                                                    Library Jobs
                                                    <span class="caret"></span>
                                                </a>
                                                <ul id="job_library" class="dropdown-menu">
                                                    <!-- stock library go here -->
                                                </ul>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="col-md-3 well well-sm">
                                        <h3>
                                            History
                                            <small>
                                                <a href="#" data-toggle="modal" data-target="#history_modal" data-backdrop="true">
                                                    show all
                                                </a>
                                            </small>
                                        </h3>
                                        <table id="job_history" class="table table-hover table-condensed">
                                            <thead>
                                                <tr>
                                                    <th>Name</th>
                                                    <th>Duration</th>
                                                </tr>
                                            </thead>
                                            <tfoot>
                                                <tr class="active">
                                                    <th>Total</th>
                                                    <th id="total_job_duration">...</th>
                                                </tr>
                                            </tfoot>
                                            <tbody></tbody>
                                        </table>
                                    </div>
                                </div>
                                <div id="tab_import" class="tab-pane">
                                    <div class="well clearfix" style="width:650px">
                                        <div class="row" style="margin-left:0px">
                                            <div class="btn-group pull-left">
                                                <button id="file_import_btn" class="btn btn-info btn-lg" data-loading-text="loading..." autocomplete="off">
                                                    <i class="glyphicon glyphicon-folder-open" style="margin-right:5px;"></i>
                                                    Import
                                                </button>
                                                <button class="btn btn-info btn-lg dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>
                                                <ul class="dropdown-menu">
                                                    <li><a id="svg_import_72_btn" href="#">Import 72dpi SVG</a></li>
                                                    <li><a id="svg_import_90_btn" href="#">Import 90dpi SVG</a></li>
                                                    <li><a id="svg_import_96_btn" href="#">Import 96dpi SVG</a></li>
                                                    <li class="divider"></li>
                                                    <li><a id="svg_import_nop_btn" href="#">Import without Optimizing</a></li>
                                                </ul>
                                            </div>
                                            <div id="dpi_import_info" class="pull-left" style="margin-top: 23px; margin-left: 15px;"></div>
                                            <div class="pull-left">
                                                <form id="svg_upload_form" action="#" onsubmit="return false;">
                                                    <input type="file" id="svg_upload_file" name="data" style="visibility:hidden; position:fixed">
                                                </form>
                                            </div>
                                        </div>
                                        <div id="import_canvas_container" style="margin-top:16px;"></div>
                                        <div id="canvas_properties">
                                            <div class="colorbtns"></div>
                                        </div>
                                        <div class="pull-left">
                                            <button id="import_to_queue" class="btn btn-primary btn-lg" style="margin-top:16px">
                                            <i class="glyphicon glyphicon-th-list"></i> Add to Queue
                                            </button>
                                        </div>
                                        <div class="pull-left" style="margin-top:27px; margin-left:20px">
                                            under name
                                        </div>
                                        <div class="pull-left" style="margin-top:22px; margin-left:10px">
                                            <input type="text" id="import_name" style="width:240px; padding-left:5px;" placeholder="Name...">
                                        </div>
                                        </div> <!--end of well-->
                                        <div class="alert alert-warning" style="width:400px">
                                            <a class="close" data-dismiss="alert">×</a>
                                            <strong>Note!</strong> Set page size in your SVG vector app to <b id="bed_size_note"></b>.
                                        </div>
                                        <div class="alert alert-warning" style="width:400px">
                                            <a class="close" data-dismiss="alert">×</a>
                                            <strong>Note!</strong> Set cutting parameters in the SVG file with <a href="http://www.lasersaur.com/manual/lasertags">LaserTags</a>.
                                        </div>
                                </div> <!-- end of import tab -->
                                <div id="tab_mover" class="tab-pane" style="margin-left:0px">
                                    <div class="well" style="width:650px">
                                        <div class="row" style="margin-left:0px">
                                            <div id="cutting_area" style="position:relative; width:610px; height:305px; border:1px dashed #aaaaaa;">
                                                <div id="coordinates_info" style="margin:4px"></div>
                                                <div id="offset_area" style="display:none; position:absolute; top:100px; left:100px; width:100px; height:100px; border-top:1px dashed #aaaaaa; border-left:1px dashed #aaaaaa">
                                                    <div id="offset_info" style="margin:4px"></div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row" style="width:475px; margin-left:auto; margin-right:auto; margin-top:20px">
                                            <div id="seek_feed_btns" class="btn-group pull-left" data-toggle="buttons-radio">
                                                <button id="seek_btn" class="btn btn-primary active">Move</button>
                                                <button id="feed_btn" class="btn btn-primary">Cut</button>
                                            </div>
                                            <div id="intensity_input_div" class="input-group pull-left" style="margin-left:8px; margin-top:16px; display: inline;">
                                                <span class="input-group-addon" style="margin-right:-5px; display: inline;">%</span>
                                                <input id="intensity_field" type="textfield" value="0" style="width:26px; display:none">
                                                <input id="intensity_field_disabled" type="textfield" class="disabled" disabled="" value="0" style="width:26px;">
                                            </div>
                                            <div id="feedrate_btns" class="btn-group pull-right" data-toggle="buttons-radio">
                                                <button id="feedrate_btn_slow" class="btn btn-primary ">slow</button>
                                                <button id="feedrate_btn_medium" class="btn btn-primary ">medium</button>
                                                <button id="feedrate_btn_fast" class="btn btn-primary active">fast</button>
                                            </div>
                                            <div class="input-group pull-right" style="margin-right:8px; margin-top:16px; display: inline;">
                                                <input id="feedrate_field" type="textfield" value="8000" style="width:40px;">
                                                <span class="input-group-addon" style="margin-left:-5px; display: inline;">mm/min</span>
                                            </div>
                                        </div>
                                        <div class="row clearfix jog_btns" style="width:400px; margin-left:auto; margin-right:auto; margin-top:16px">
                                            <div class="pull-left" style="width:140px; height:130px; background-color:#dddddd; padding-top: 20px;">
                                                <div class="row" style="width:44px; margin-left:auto; margin-right:auto;">
                                                    <button id="jog_up_btn" class="btn btn-default btn-lg">
                                                        <i class="glyphicon glyphicon-arrow-up"></i>
                                                    </button>
                                                </div>
                                                <div class="row" style="width:100px; margin-left:auto; margin-right:auto; margin-top:8px;">
                                                    <button id="jog_left_btn" class="btn btn-default btn-lg pull-left"><i class="glyphicon glyphicon-arrow-left"></i></button>
                                                    <button id="jog_right_btn" class="btn btn-default btn-lg pull-right"><i class="glyphicon glyphicon-arrow-right"></i></button>
                                                </div>
                                                <div class="row" style="width:44px; margin-left:auto; margin-right:auto; margin-top:8px">
                                                    <button id="jog_down_btn" class="btn btn-default btn-lg"><i class="glyphicon glyphicon-arrow-down"></i></button>
                                                </div>
                                            </div>
                                            <div class="pull-right" style="width:168px; height:130px; background-color:#dddddd; padding-top: 15px;">
                                                <div class="btn-group" style="margin-bottom:20px; margin-left: 15px;">
                                                    <button id="location_set_btn" class="btn btn-primary btn-sm" style="padding:5px;">
                                                        <span id="loc_move_cut_word">Move</span> To
                                                    </button>
                                                    <button id="origin_set_btn" class="btn btn-primary btn-sm" style="padding:5px;">Offset To</button>
                                                </div>
                                                <div class="input-group pull-left" style="display: inline;">
                                                    <span class="input-group-addon" style="margin-right:-5px;display: inline;">x</span>
                                                    <input id="x_location_field" type="textfield" value="0" style="width:48px;">
                                                </div>
                                                <div class="input-group pull-left" style="margin-left:4px; display: inline;">
                                                    <span class="input-group-addon" style="margin-right:-5px;display: inline;">y</span>
                                                    <input id="y_location_field" type="textfield" value="0" style="width:42px;">
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row" style="width:210px; margin-left:auto; margin-right:auto;">
                                            <button id="air_on_btn" class="btn btn-primary">Air Assist On</button>
                                            <button id="air_off_btn" class="btn btn-primary">Air Assist Off</button>
                                        </div>
                                    </div>
                                    <div class="alert alert-warning" style="width:400px">
                                        <a class="close" data-dismiss="alert">×</a>
                                        <strong>Note!</strong> Set an offset by shift-clicking in the work area.
                                    </div>
                                    <div class="alert alert-warning" style="width:400px">
                                        <a class="close" data-dismiss="alert">×</a>
                                        <strong>Note!</strong> User arrow keys to jog. De/increase step with alt and shift.
                                    </div>
                                </div> <!-- end of mover tab -->
                                <div id="tab_logs" class="tab-pane active">
                                    <div class="alert alert-warning" style="margin:5px; display:none">
                                        <a class="close" data-dismiss="alert">×</a>
                                        Log, most recent messages first:
                                    </div>
                                    <div id="log_content" style="clear:both; overflow:auto; display:none">
                                        <!-- log -->
                                    </div>
                                </div> <!-- end of log tab -->
                                <!--content end-->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal -->
        <div class="modal fade" id="history_modal" tabindex="-1" role="dialog" aria-labelledby="history_modal_title">
          <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title" id="history_modal_title">Job History</h4>
              </div>
              <div class="modal-body" style="overflow:auto; max-height:500px;">
                <table id="job_history_big" class="table table-striped">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Start</th>
                            <th>End</th>
                            <th>Duration</th>
                            <th>Lines of GCode</th>
                        </tr>
                    </thead>
                    <tfoot>
                        <tr class="active">
                            <th></th>
                            <th></th>
                            <th>Total Duration</th>
                            <th id="total_job_duration_big">...</th>
                            <th></th>
                        </tr>
                    </tfoot>
                    <tbody></tbody>
                </table>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div>


        <script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
        <script src="/js/jquery.toastmessage.js"></script>
        <script src="/js/jquery.hotkeys.js"></script>
        <script src="/js/settings.js"></script>
        <script src="/js/app_svgreader.js"></script>
        <script src="/js/app_datahandler.js"></script>
        <script src="/js/app_canvas.js"></script>
        <script src="/js/app.js"></script>
        <script src="/js/app_laserjobs.js"></script>
        <script src="/js/app_mover.js"></script>
        <script src="/js/app_import.js"></script>
        <script src="/js/ripples.min.js"></script>
        <script src="/js/material.min.js"></script>
        <script src="/js/dateformat.js"></script>
        <script>
            $(document).ready(function() {
                $.material.init();
            });
        </script>
    </body>
</html>