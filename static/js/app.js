
var hardware_ready_state = false;
var firmware_version_reported = false;
var lasaurapp_version_reported = false;
var progress_not_yet_done_flag = false;

//Popup Messages
(function($){
  $.fn.uxmessage = function(kind, text, max_length) {
    if (max_length == null) {
      max_length = 100;
    }

    if (text.length > max_length) {
      text = text.slice(0,max_length) + '\n...'
    }

    text = text.replace(/\n/g,'<br>')

    if (kind == 'notice') {
      $('#log_content').prepend('<div class="log_item log_notice well-sm" style="display:none">' + text + '</div>');
      $('#log_content').children('div').first().show('blind');
      if ($("#log_content").is(':hidden')) {
        $().toastmessage('showNoticeToast', text);
      }
    } else if (kind == 'success') {
      $('#log_content').prepend('<div class="log_item log_success well-sm" style="display:none;">' + text + '</div>');
      $('#log_content').children('div').first().show('blind');
      if ($("#log_content").is(':hidden')) {
        $().toastmessage('showSuccessToast', text);
      }
    } else if (kind == 'warning') {
      $('#log_content').prepend('<div class="log_item log_warning well-sm" style="display:none">' + text + '</div>');
      $('#log_content').children('div').first().show('blind');
      if ($("#log_content").is(':hidden')) {
        $().toastmessage('showWarningToast', text);
      }
    } else if (kind == 'error') {
      $('#log_content').prepend('<div class="log_item log_error well-sm" style="display:none">' + text + '</div>');
      $('#log_content').children('div').first().show('blind');
      if ($("#log_content").is(':hidden')) {
        $().toastmessage('showErrorToast', text);
      }
    }

    while ($('#log_content').children('div').length > 200) {
      $('#log_content').children('div').last().remove();
    }

  };
})(jQuery);


function send_gcode(gcode, success_msg, progress, name) {
    if (typeof gcode === "string" && gcode != '') {
      $.ajax({
        type: "POST",
        url: "/gcode",
        data: {'name': name, 'job_data':gcode},
        success: function (data) {
          if (data === "__ok__") {
            $().uxmessage('success', success_msg);
            if (progress) {
              // show progress bar, register live updates
              if ($("#progressbar").children().first().width() == 0) {
                $("#progressbar").children().first().width('5%');
                $("#progressbar").show();
                progress_not_yet_done_flag = true;
                setTimeout(update_progress, 2000);
              }
            }
          } else {
            $().uxmessage('error', "Backend error: " + data);
          }
        },
        error: function (data) {
          $().uxmessage('error', "Timeout. LasaurApp server down?");
        },
        complete: function (data) {
          // future use
        }
      });
    } else {
      $().uxmessage('error', "No gcode.");
    }
}


function update_progress() {
  $.get('/queue_pct_done', function(data) {
    if (data.length > 0) {
      var pct = parseInt(data);
      $("#progressbar").children().first().width(pct+'%');
      setTimeout(update_progress, 2000);
    } else {
      if (progress_not_yet_done_flag) {
        $("#progressbar").children().first().width('100%');
        $().uxmessage('notice', "Done.");
        progress_not_yet_done_flag = false;
        setTimeout(update_progress, 2000);
      } else {
        $('#progressbar').hide();
        $("#progressbar").children().first().width(0);


        poll_job_history();
      }
    }
  });
}


function open_bigcanvas(scale, deselectedColors) {
  var w = scale * app_settings.canvas_dimensions[0];
  var h = scale * app_settings.canvas_dimensions[1];
  $('#container').before('<a id="close_big_canvas" href="#"><canvas id="big_canvas" width="'+w+'px" height="'+h+'px" style="border:1px dashed #aaaaaa;"></canvas></a>');
  var mid = $('body').innerWidth()/2.0-30;
  $('#close_big_canvas').click(function(e){
    close_bigcanvas();
    return false;
  });
  $("html").on('keypress.closecanvas', function (e) {
    if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13) ||
        (e.which && e.which == 27) || (e.keyCode && e.keyCode == 27)) {
      // on enter or escape
      close_bigcanvas();
      return false;
    } else {
      return true;
    }
  });
  // $('#big_canvas').focus();
  $('#container').hide();
  var bigcanvas = new Canvas('#big_canvas');
  // DataHandler.draw(bigcanvas, 4*app_settings.to_canvas_scale, getDeselectedColors());
  if (deselectedColors === undefined) {
    DataHandler.draw(bigcanvas, scale*app_settings.to_canvas_scale);
  } else {
    DataHandler.draw(bigcanvas, scale*app_settings.to_canvas_scale, deselectedColors);
  }
}


function close_bigcanvas() {
  $('#big_canvas').remove();
  $('#close_big_canvas').remove();
  $('html').off('keypress.closecanvas');
  delete bigcanvas;
  $('#container').show();
}


//function generate_download(filename, filedata) {
//  $.ajax({
//    type: "POST",
//    url: "/stash_download",
//    data: {'filedata': filedata},
//    success: function (data) {
//      window.open("/download/" + data + "/" + filename, '_blank');
//    },
//    error: function (data) {
//      $().uxmessage('error', "Timeout. LasaurApp server down?");
//    },
//    complete: function (data) {
//      // future use
//    }
//  });
//}


function getDurationString(durationSeconds) {
    var hours   = Math.floor(durationSeconds / 3600);
    var minutes = Math.floor((durationSeconds - (hours * 3600)) / 60);
    var seconds = durationSeconds - (hours * 3600) - (minutes * 60);
    return hours + 'h ' + minutes + 'min ' + seconds + 's ';
}


function poll_job_history() {
  console.log("poll_job_history");

  $.getJSON('/jobs/history?limit=10', function(history) {
    $('#job_history tbody').empty();

    for (var i in history) {
      var job = history[i];
      var date = new Date(job.start.$date).format('dd.mm.yyyy hh:MM:ss');
      var duration = getDurationString(job.duration);
      var row = $('<tr style="cursor: pointer;" title="'+date+'" data-toggle="tooltip" data-placement="right" onclick="show_job('+i+')"/>');
      row.append($('<td class="name" />').append($('<span/>').text(job.name)));
      row.append($('<td/>').append($('<span/>').text(duration)));
      $('#job_history tbody').append(row);
    }

    if (history.length > 0) {
      $('#total_job_duration').text(getDurationString(history[0].total));
    }

    $('[data-toggle="tooltip"]').tooltip({ container: 'body' });
  });
}

function show_job(i) {
    $.getJSON('/jobs/history', function(history) {
        job = history[i];
        product =
        $('#job_modal_title').text(job['name']);
        $('#job_comment_').text(job['comment']);
        $('#job_start_time').text(new Date(job.start.$date).format('dd.mm.yyyy hh:MM:ss'));
        $('#job_end_time').text(new Date(job.end.$date).format('dd.mm.yyyy hh:MM:ss'));
        duration = job['duration']
        $('#job_duration').text(Math.floor(duration / 60) + ":" + ((duration % 60 < 10) ? "0" : "") + (duration % 60));
        $('#job_modal').modal('show');
    });
}

$('#login_btn').click(function(){
  $.getJSON("/login", {'login_email': $('#login_email').val(), 'login_password': $('#login_password').val()}, function(e){

    if(e['result'] == true){ //ToDo: Better handling
      username = e['payload']
      $('#account_drop').html(username + '<b class="caret">');
      $('#job_client').html(username);
      $('#login_modal').modal('hide');
    }else {
      $('#login_text').text(e);
    }
  });
});

$('#login_modal').bind('keypress', function(e) {
    if(e.keyCode==13){
        $('#login_btn').click();
    }
});

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////



$(document).ready(function(){
  $().uxmessage('notice', "Frontend started.");

  $('#feedrate_field').val(app_settings.max_seek_speed);
  if (!app_settings.air_assist_enabled) {
    $('#air_assist_group').hide();
  }

  $('#tab_logs_button').click(function(){
    $('#log_content').show();
    $('#tab_logs div.alert').show();
  });

  $('#tab_sensors_button').click(function(){
    $('#sensor_values').show();
  });

  if (app_settings.custom_buttons) {
    for (var i = 0; i < app_settings.custom_buttons.length; i++) {
      var btn = app_settings.custom_buttons[i];
      var btnObj = $('<button id="custom_button_' + i + '" class="btn btn-default custom_button" type="submit" title="' + btn.title + '"></button>');
      btnObj.html('<i class="glyphicon glyphicon-' + btn.icon + '"></i>');

      if (btn.default_on) {
        btnObj.addClass('btn-success');
      }
      btnObj.data('def', btn);

      btnObj.click(function() {
        var def = $(this).data('def');
        if (def.toggle) {
          if ($(this).hasClass('btn-success')) {
            $(this).removeClass('btn-success');

            send_gcode(def.gcode_disable, def.disable_message);
          } else {
            $(this).addClass('btn-success');

            send_gcode(def.gcode_enable, def.enable_message);
          }
        } else {
          send_gcode(def.gcode_enable);
        }
      });
      $('#button_container').append(btnObj);
    }
  }


  //////// serial connect and pause button ////////
  var connect_btn_state = false;
  var connect_btn_in_hover = false;
  var pause_btn_state = false;

  function connect_btn_set_state(is_connected) {
    if (is_connected) {
      connect_btn_state = true;
      $("#connect_btn").removeClass("btn-danger");
      $("#connect_btn").removeClass("btn-warning");
      $("#connect_btn").addClass("btn-success");

      if (!connect_btn_in_hover) {
          $("#connect_btn").html("Connected");
      }
    } else {
      connect_btn_state = false
      if (!connect_btn_in_hover) {
        $("#connect_btn").html("Disconnected");
      }
      $("#connect_btn").removeClass("btn-danger");
      $("#connect_btn").removeClass("btn-success");
      $("#connect_btn").addClass("btn-warning");
    }
  }

  // get hardware status
  function poll_hardware_status() {
    $.getJSON('/status', function(data) {
      // pause status
      if (data.paused) {
        pause_btn_state = true;
        $("#pause_btn").addClass("btn-primary");
        $("#pause_btn").html('<i class="glyphicon glyphicon-play"></i>');
      } else {
        pause_btn_state = false;
        $("#pause_btn").removeClass("btn-warning");
        $("#pause_btn").removeClass("btn-primary");
        $("#pause_btn").html('<i class="glyphicon glyphicon-pause"></i>');
      }
      // serial connected
      if (data.serial_connected) {
        connect_btn_set_state(true);
      } else {
        connect_btn_set_state(false);
      }

      // ready state
      id_card_status = data.id_card_status;
      if (data.ready) {
        hardware_ready_state = true;
        $("#connect_btn").html("Ready").removeClass("btn-warning");
      } else {
        if (data.serial_connected) {
          $("#connect_btn").html("Busy");
        }
        hardware_ready_state = false;
      }

      // door, chiller, power, limit, buffer
      if (data.serial_connected) {
        if (data.door_open) {
          $('#door_status_btn').removeClass('btn-success').addClass('btn-warning');
          // $().uxmessage('warning', "Door is open!");
        } else {
          $('#door_status_btn').removeClass('btn-warning').addClass('btn-success');
        }
        if (data.chiller_off) {
          $('#chiller_status_btn').removeClass('btn-success').addClass('btn-warning');
          // $().uxmessage('warning', "Chiller is off!");
        } else {
          $('#chiller_status_btn').removeClass('btn-warning').addClass('btn-success');
        }
        if (data.power_off) {
          $().uxmessage('error', "Power is off!");
          $().uxmessage('notice', "Turn on Lasersaur power then run homing cycle to reset.");
        }
        if (data.limit_hit) {
          $().uxmessage('error', "Limit hit!");
          $().uxmessage('notice', "Run homing cycle to reset stop mode.");
        }
        if (data.buffer_overflow) {
          $().uxmessage('error', "Rx Buffer Overflow!");
          $().uxmessage('notice', "Please report this to the author of this software.");
        }
        if (data.transmission_error) {
          $().uxmessage('error', "Transmission Error!");
          $().uxmessage('notice', "If this happens a lot tell the author of this software.");
        }
        if (data.x && data.y) {
          // only update if not manually entering at the same time
          if (!$('#x_location_field').is(":focus") &&
              !$('#y_location_field').is(":focus") &&
              !$('#location_set_btn').is(":focus") &&
              !$('#origin_set_btn').is(":focus"))
          {
            var x = parseFloat(data.x).toFixed(2) - app_settings.table_offset[0];
            $('#x_location_field').val(x.toFixed(2));
            $('#x_location_field').animate({
              opacity: 0.5
            }, 100, function() {
              $('#x_location_field').animate({
                opacity: 1.0
              }, 600, function() {});
            });
            var y = parseFloat(data.y).toFixed(2) - app_settings.table_offset[1];
            $('#y_location_field').val(y.toFixed(2));
            $('#y_location_field').animate({
              opacity: 0.5
            }, 100, function() {
              $('#y_location_field').animate({
                opacity: 1.0
              }, 600, function() {});
            });
          }
        }
        if (data.firmware_version && !firmware_version_reported) {
          $().uxmessage('notice', "Firmware v" + data.firmware_version);
          $('#firmware_version').html(data.firmware_version);
          firmware_version_reported = true;
        }
      }
      if (data.lasaurapp_version && !lasaurapp_version_reported) {
        $().uxmessage('notice', "LasaurApp v" + data.lasaurapp_version);
        $('#lasaurapp_version').html(data.lasaurapp_version);
        lasaurapp_version_reported = true;
      }
      // schedule next hardware poll
      setTimeout(function() {poll_hardware_status()}, 4000);
    }).error(function() {
      // lost connection to server
      connect_btn_set_state(false);
      // schedule next hardware poll
      setTimeout(function() {poll_hardware_status()}, 8000);
    });
  }
  // kick off hardware polling
  poll_hardware_status();

  poll_job_history();

  connect_btn_width = $("#connect_btn").width();
  $("#connect_btn").width(connect_btn_width);
  $("#connect_btn").click(function(e){
    if (connect_btn_state == true) {
      $.get('/serial/0', function(data) {
        if (data != "") {
          connect_btn_set_state(false);
        } else {
          // was already disconnected
          connect_btn_set_state(false);
        }
        $("#connect_btn").html("Disconnected");
      });
    } else {
      $("#connect_btn").html('Connecting...');
      $.get('/serial/1', function(data) {
        if (data != "") {
          connect_btn_set_state(true);
          $("#connect_btn").html("Connected");
        } else {
          // failed to connect
          connect_btn_set_state(false);
          $("#connect_btn").removeClass("btn-warning");
          $("#connect_btn").addClass("btn-danger");
        }
      });
    }
    e.preventDefault();
  });
  $("#connect_btn").hover(
    function () {
      connect_btn_in_hover = true;
      if (connect_btn_state) {
        $(this).html("Disconnect");
      } else {
        $(this).html("Connect");
      }
      $(this).width(connect_btn_width);
    },
    function () {
      connect_btn_in_hover = false;
      if (connect_btn_state) {
        $(this).html("Connected");
      } else {
        $(this).html("Disconnected");
      }
      $(this).width(connect_btn_width);
    }
  );

  $("#pause_btn").tooltip({placement:'bottom', delay: {show:500, hide:100}});
  $("#pause_btn").click(function(e){
    if (pause_btn_state == true) {  // unpause
      $.get('/pause/0', function(data) {
        if (data == '0') {
          pause_btn_state = false;
          $("#pause_btn").removeClass('btn-primary');
          $("#pause_btn").removeClass('btn-warning');
          $("#pause_btn").html('<i class="glyphicon glyphicon-pause"></i>');
          $().uxmessage('notice', "Continuing...");
        }
      });
    } else {  // pause
      $("#pause_btn").addClass('btn-warning');
      $.get('/pause/1', function(data) {
        if (data == "1") {
          pause_btn_state = true;
          $("#pause_btn").removeClass("btn-warning");
          $("#pause_btn").addClass('btn-primary');
          $("#pause_btn").html('<i class="glyphicon glyphicon-play"></i>');
          $().uxmessage('notice', "Pausing in a bit...");
        } else if (data == '0') {
          $("#pause_btn").removeClass("btn-warning");
          $("#pause_btn").removeClass("btn-primary");
          $().uxmessage('notice', "Not pausing...");
        }
      });
    }
    e.preventDefault();
  });
  //\\\\\\ serial connect and pause button \\\\\\\\


  $("#cancel_btn").tooltip({placement:'bottom', delay: {show:500, hide:100}});
  $("#cancel_btn").click(function(e) {
    var gcode = '!\n';  // ! is enter stop state char
    // $().uxmessage('notice', gcode.replace(/\n/g, '<br>'));
    send_gcode(gcode, "Stopping ...", false);
    var delayedresume = setTimeout(function() {
      var gcode = '~\nG90\nM81\nG0X0Y0F'+app_settings.max_seek_speed+'\n'  // ~ is resume char
      // $().uxmessage('notice', gcode.replace(/\n/g, '<br>'));
      send_gcode(gcode, "Resetting ...", false);
    }, 1000);
    e.preventDefault();
  });

  $("#homing_cycle").tooltip({placement:'bottom', delay: {show:500, hide:100}});
  $("#homing_cycle").click(function(e){
    var gcode = '!\n'  // ! is enter stop state char
    // $().uxmessage('notice', gcode.replace(/\n/g, '<br>'));
    send_gcode(gcode, "Resetting ...", false);
    var delayedresume = setTimeout(function() {
      var gcode = '~\nG30\n'  // ~ is resume char
      // $().uxmessage('notice', gcode.replace(/\n/g, '<br>'));
      send_gcode(gcode, "Homing cycle ...", false);
    }, 1000);
    e.preventDefault();

  });

  $("#go_to_origin").tooltip({placement:'bottom', delay: {show:500, hide:100}});
  $("#go_to_origin").click(function(e){
    var gcode;
    if(e.shiftKey) {
      // also reset offset
      reset_offset();
    }
    gcode = 'G90\nG0X0Y0F'+app_settings.max_seek_speed+'\n'
    // $().uxmessage('notice', gcode);
    send_gcode(gcode, "Going to origin ...", false);
    e.preventDefault();
  });

  $("#reset_atmega").click(function(e){
    $.get('/reset_atmega', function(data) {
      if (data != "") {
        $().uxmessage('success', "Atmega restarted!");
        firmware_version_reported = false;
      } else {
        $().uxmessage('error', "Atmega restart failed!");
      }
    });
    e.preventDefault();
  });


  /// tab shortcut keys /////////////////////////
  $(document).on('keypress', null, 'p', function(e){
    $('#pause_btn').trigger('click');
    return false;
  });

  $(document).on('keypress', null, '0', function(e){
    $('#go_to_origin').trigger('click');
    return false;
  });

  var cancel_modal_active = false;
  $(document).on('keyup', null, 'esc', function(e){
    if (cancel_modal_active === true) {
      $('#cancel_modal').modal('hide');
      cancel_modal_active = false;
    } else {
      $('#cancel_modal').modal('show');
      $('#really_cancel_btn').focus();
      cancel_modal_active = true;
    }
    return false;
  });

  $('#really_cancel_btn').click(function(e){
    $('#cancel_btn').trigger('click');
    $('#cancel_modal').modal('hide');
    cancel_modal_active = false;
  });



  /// tab shortcut keys /////////////////////////

  $(document).on('keypress', null, 'j', function(e){
    $('#tab_jobs_button').trigger('click');
    return false;
  });

  $(document).on('keypress', null, 'i', function(e){
    $('#tab_import_button').trigger('click');
    return false;
  });

  $(document).on('keypress', null, 'm', function(e){
    $('#tab_mover_button').trigger('click');
    return false;
  });

  $(document).on('keypress', null, 'l', function(e){
    $('#tab_logs_button').trigger('click');
    return false;
  });

  $(document).on('keypress', null, 's', function(e){
    $('#tab_sensors_button').trigger('click');
    return false;
  });

  $('#history_modal').on('show.bs.modal', function (e) {

    $.getJSON('/jobs/history', function(history) {
      $('#history_modal tbody').empty();
      for (var i in history) {
        var job = history[i];
        var start_date = new Date(job.start.$date).format('dd.mm.yyyy hh:MM:ss');
        var end_date = new Date(job.end.$date).format('dd.mm.yyyy hh:MM:ss');
        var duration = getDurationString(job.duration);

        var row = $('<tr/>');
        row.append($('<td />').append($('<span class="cell row-1" />').text(job.name).attr('data-original-title', job.name)));
        row.append($('<td />').append($('<span class="cell row-2" />').text(job.client)));
        row.append($('<td />').append($('<span class="cell row-3" />').text(start_date)));
        row.append($('<td />').append($('<span class="cell row-4" />').text(end_date)));
        //row.append($('<td />').append($('<span class="cell row-5" />').text(job.lines)));
        row.append($('<td />').append($('<span class="cell row-6" />').text(duration)));
        row.data('duration', job.duration);
        $('#history_modal tbody').append(row);
      }

      if (history.length > 0) {
        $('#total_job_duration_big').text(getDurationString(history[0].total));
      }

      $('#selected_history_label').hide();

      $('#history_modal tbody span.cell').tooltip({ container: 'body' });
    });
  });

  $('#job_history_big tbody').on('click', 'tr', function() {
    $(this).toggleClass('selected');

    var selected = $('#job_history_big tbody tr.selected');
    if (selected.length <= 0) {
      $('#selected_history_label').hide();
    } else {
      $('#selected_history_label').show();

      var duration = 0;
      selected.each(function(i, row) {
        duration += $(row).data('duration');
      });

      var durationString = getDurationString(duration);
      $('#selected_history_label .badge').text(durationString);
    }
  });
});  // ready


 $('#material_modal').on('show.bs.modal', function (e) {
    $('#job_material_qty_input').val(1);
    $('#job_materials').val([]);
    $.post('/checkLogin', function(e){
        if(e=="true")
            $('#job_client_input').val("yes");
    });
    $('#material_selected').removeClass("btn-primary");
});


var odoo_products = null;
var odoo_services = null;

$(document).ready(function() {
    $.post('/checkLogin', function(e){
        if(e=="true"){
             $('#account_drop').html("yes " + '<b class="caret">');
        }
    });

    odoo_product = 0;
    odoo_service = 0;
    job_comment = "";

    $.getJSON('/interface/getData', function(data){
        odoo_services = data['usage'];
        console.log(odoo_services)
        //try{
        var select_list = document.getElementById('job_services');
        for (var i in odoo_services) {
            var s = odoo_services[i];
            var option = document.createElement("option");
            option.value = s['id'];
            option.innerHTML = s['name']
              + "  " + s['price'] + " €/min";
            select_list.appendChild(option);
        }
        select_list.size = Math.min(odoo_services.length, select_list.size);

        odoo_products = data['materials'];
        var select_list = document.getElementById("job_materials");
        for (var i in odoo_products) {
            var s = odoo_products[i];
            var option = document.createElement("option");
            option.value = s['id'];
            option.innerHTML = s['name'] + (s['price'] != 0 ? "  " + s['price'] + " €" : "");
            select_list.appendChild(option);
        }
    });
  });

var material_form_ok_clickable = false;

$('#material_form').on('input',function(){
    if($('#job_materials').val() != null && $('#job_services').val() != null && $('#job_client_input').val() != "") {
        material_form_ok_clickable = true;
        $('#material_selected').addClass("btn-primary");
    } else {
        material_form_ok_clickable = false;
        $('#material_selected').removeClass("btn-primary");
    }
});

$('#job_materials').dblclick(function(){
    $('#job_materials').trigger("click");
    if(material_form_ok_clickable)
        $("#material_selected").trigger("click");
});

var default_cut_speed = 1500;
var default_cut_intensity = 100;
var default_engrave_speed = 4000;
var default_engrave_intensity = 20;

setInterval(function(){
    $.getJSON("/sensors", function(data){
        for(var i in data) {
            s = data[i]
            str += s['name'] + ": " + s['value'] + " " + s['unit'] + "<br>";
        }
        $('#sensor_values').html(str);
    });
}, 3000);

$("#material_selected").click(function(e) {
    if(!material_form_ok_clickable)
      return;
    odoo_product_id = $('#job_materials').val();
    odoo_service_id = $('#job_services').val();
    job_comment = $('#job_comment_input').val();
//    job_client = $('#job_client_input').html();

    for(var product in odoo_products) {
        if(odoo_products[product]['id'] == odoo_product_id) {
            product = odoo_products[product];
            default_cut_speed = product['machine_parameter_1'];
            default_cut_intensity = product['machine_parameter_2'];
            default_engrave_speed = product['machine_parameter_3'];
            default_engrave_intensity = product['machine_parameter_4'];
        }
    }
    $("#material_modal").modal('hide');
});

$('#create_account_btn').click(function(){
    window.open("https://ldap.fablab-karlsruhe.de", "_blank");
});

$('#reset_pw_btn').click(function(){
    window.open("https://ldap.fablab-karlsruhe.de", "_blank");
});


$('#job_submit').click(function(e) {
    if($('#job_submit').hasClass('btn-primary')) {
         $.post('/checkLogin', function(e){
            if(e == "true") {
                $("#qty_modal").modal('show');
            } else {
                $("#login_modal").modal('show');
            }
        });
    }
});

$("#qty_btn_1").click(function(e) {
    $("#qty_modal").modal('hide');
    job_material_qty = 1;
    send_erp_data();
});

$("#qty_btn_0").click(function(e) {
    $("#qty_modal").modal('hide');
    job_material_qty = 0;
    send_erp_data();
});

$("#qty_btn_custom").click(function(e) {
    $("#qty_modal").modal('hide');
    job_material_qty = $('#qty_quantity').val();
    send_erp_data();
});

$('#really_submit_job_btn').click(function() {
  send_erp_data();
});

/// PASSES //////////////////////////////////////


function setDefaultCut(passnum){
    //$('#feedrate_'+passnum).value = 100;
    feedrate_field = document.getElementById('feedrate_' + passnum);
    feedrate_field.value = default_cut_speed;
    intensity_field = document.getElementById('intensity_' + passnum);
    intensity_field.value = default_cut_intensity;
}

function setDefaultEngrave(passnum){
    //$('#feedrate_'+passnum).value = 100;
    feedrate_field = document.getElementById('feedrate_' + passnum);
    feedrate_field.value = default_engrave_speed;
    intensity_field = document.getElementById('intensity_' + passnum);
    intensity_field.value = default_engrave_intensity;
}


jQuery.fn.shake = function(intShakes, intDistance, intDuration) {
    this.each(function() {
        $(this).css("position","relative");
        for (var x=1; x<=intShakes; x++) {
        $(this).animate({left:(intDistance*-1)}, (((intDuration/intShakes)/4)))
    .animate({left:intDistance}, ((intDuration/intShakes)/2))
    .animate({left:0}, (((intDuration/intShakes)/4)));
    }
  });
  return this;
};
