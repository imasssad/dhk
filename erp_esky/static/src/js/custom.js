odoo.define('erp_esky.custom', function(require) {
"use strict";
   var publicWidget = require('web.public.widget');
   var Widget = require("web.Widget");
    var core = require("web.core");
    var QWeb = core.qweb;
    var _t = core._t;
    var latitude = "";
    var longitude = "";
    window.location_data = "";

    publicWidget.registry.HrAttendances.include({
        start: function () {
            var self = this;
            // Get latitude longitude
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(setCurrentPosition, positionError, {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0,
                });

                function setCurrentPosition(position) {
                    latitude = position.coords.latitude;
                    longitude = position.coords.longitude;
                }
                function positionError(error) {
                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            console.error("User denied the request for Geolocation.");
                            break;
                        case error.POSITION_UNAVAILABLE:
                            console.error("Location information is unavailable.");
                            break;
                        case error.TIMEOUT:
                            console.error("The request to get user location timed out.");
                            break;
                        case error.UNKNOWN_ERROR:
                            console.error("An unknown error occurred.");
                            break;
                    }
                }
            } else {
                console.log("API Not Supported.");
            }
            return this._super.apply(this, arguments);
        },
        _update_attendance: function (ev) {
            var self = this;
            const employee_id = $(ev.currentTarget).data('id');
            var message = $(".checkin_message").val();

            console.log("latitude : ",latitude)
            console.log("longitude : ",longitude)

            if(!latitude || !longitude){
                alert("Please Check your browser Settings and Allow Location !")
	        }else{
	            this._rpc({
	                model: "hr.employee",
	                method: "sh_attendance_manual",
	                args: [[employee_id], [message, latitude, longitude], "hr_attendance.hr_attendance_action_my_attendances"],
	            }).then(function (result) {
	                if (result.action) {
	                    self.do_action(result.action);
	                } else if (result.warning) {
	                    self.do_warn(result.warning);
	                }
	                window.location.reload();
	            });
	        }
        },
    });
});