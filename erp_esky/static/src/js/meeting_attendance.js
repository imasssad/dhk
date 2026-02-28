odoo.define('erp_esky.meeting_attendance', function(require) {
"use strict";
   var publicWidget = require('web.public.widget');
   var Widget = require("web.Widget");
    var core = require("web.core");
    var QWeb = core.qweb;
    var _t = core._t;
    var latitude = "";
    var longitude = "";
    window.location_data = "";

    publicWidget.registry.HrMeetingAttendance = publicWidget.Widget.extend({
        selector: '.portal_attendance_meeting',
        events: {
            'click #meeting_attendanace_checkin': '_update_attendance_meeting',
            'click #meeting_attendanace_checkout': '_update_attendance_meeting',
        },
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
        _update_attendance_meeting: function (ev) {
            var self = this;
            const meeting_id = $(ev.currentTarget).attr("checkin-id");

            console.log("meeting_id : ",meeting_id)
            console.log("latitude : ",latitude)
            console.log("longitude : ",longitude)

            if(latitude || longitude){
	            this._rpc({
	                model: "calendar.event",
	                method: "dics_meeting_attendance",
	                args: [[parseInt(meeting_id)], ["", latitude, longitude], "hr_attendance.hr_attendance_action_my_attendances"],
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