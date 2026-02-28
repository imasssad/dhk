odoo.define('portal_attendance_knk.custom', function(require) {
"use strict";
   var publicWidget = require('web.public.widget');
   var latitude = "";
   var longitude = "";

    publicWidget.registry.HrAttendances = publicWidget.Widget.extend({
        selector: '.portal_attendance_knk',
        events: {
            'click .o_hr_attendance_sign_in_out_icon': '_update_attendance',
        },
        _update_attendance: function (ev) {
            var self = this;
            const employee_id = $(ev.currentTarget).data('id');
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(setCurrentPosition, positionError, {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0,
                });

                function setCurrentPosition(position) {
                    latitude = position.coords.latitude;
                    longitude = position.coords.longitude;
                    self._rpc({
                            model: 'hr.employee',
                            method: 'sh_attendance_manual',
                            args: [[employee_id], ["", latitude, longitude], "hr_attendance.hr_attendance_action_my_attendances"],
                        })
                        .then(function(result) {
                            if (result.action) {
                                self.do_action(result.action);
                            } else if (result.warning) {
                                self.do_warn(result.warning);
                            }
                            window.location.reload();
                        });
                }
                function positionError(error) {
                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            alert("Please Check your browser Settings and Allow Location !")
                            console.error("User denied the request for Geolocation.");
                            break;
                        case error.POSITION_UNAVAILABLE:
                            alert("Location information is unavailable.")
                            console.error("Location information is unavailable.");
                            break;
                        case error.TIMEOUT:
                            alert("The request to get user location timed out.");
                            console.error("The request to get user location timed out.");
                            break;
                        case error.UNKNOWN_ERROR:
                            alert("An unknown error occurred.");
                            console.error("An unknown error occurred.");
                            break;
                    }
                }
            } else {
                alert("API Not Supported.")
                console.log("API Not Supported.");
            }
        },
    });
});
