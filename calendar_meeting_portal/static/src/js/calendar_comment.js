odoo.define('calendar_meeting_portal.calendar_comment', function (require) {
'use strict';

	$(document).on("click", ".update_calendar_details", function () {
		$('.custom_calendar_comment').val('');
	});
	$(".hide_timesheet_comment_wizard").click(function () {
		$('.MyCustomCalendarModal').modal('hide');
    });
});

