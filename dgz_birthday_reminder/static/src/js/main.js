/** @odoo-module **/
import core from 'web.core';
import rpc from 'web.rpc';
import SystrayMenu from 'web.SystrayMenu';
import Widget from 'web.Widget';

var qweb = core.qweb;

const SystrayWidget = Widget.extend({
    template: 'DgzBirthdayReminderSystrayDropdown',
    events: {
        'click .o-dropdown': '_onClick',
    },

    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.triggerRpcAndUpdateCount();
        this._check_data();
        $(document).on('click', (event) => { if (!$(event.target).closest('.SystrayMenuContainer').length) { this.closeDropdown(); }; });
    },

    _onClick: function(ev) {
        this.triggerRpcAndUpdateCount();
        this._check_data();
        ev.stopPropagation(); var self = this; let dropBox = $(ev.currentTarget.parentElement).find('#bdy_systray_notif'); dropBox.toggle();
    },

    _check_data: function(){
        var self = this;
        rpc.query({ model: 'hr.employee', method: 'get_birthday_reminders' }).then(function(result) { self.updateBirthdayIcon(self.calculateUpcomingBirthdaysCount(result.employee_data_dict)); self.renderTemplate(result); });
    },

    calculateUpcomingBirthdaysCount: function(employeeDataDict) {
        var today = new Date(); var sevenDaysLater = new Date(today); sevenDaysLater.setDate(today.getDate() + 7); var upcomingBirthdaysCount = 0;
        for (var employeeId in employeeDataDict) { var nextBirthday = new Date(employeeDataDict[employeeId].next_birthday); if (nextBirthday = today && nextBirthday <= sevenDaysLater) { upcomingBirthdaysCount++; }; }
        return upcomingBirthdaysCount;
    },

    updateBirthdayIcon: function(count) {
        var countElement = $('.birthday-count'); if (count > 0) { countElement.text(count).show(); } else { countElement.hide(); }
    },

    renderTemplate: function(result) {
        try {
            var employeeKeys = Object.keys(result.employee_data_dict).sort((a, b) => {
                var nextBirthdayA = new Date(result.employee_data_dict[a].next_birthday);
                var nextBirthdayB = new Date(result.employee_data_dict[b].next_birthday);
                return nextBirthdayA - nextBirthdayB;
            });
            var template = qweb.render('BdySystrayDetails', { employeeKeys: employeeKeys, employee_data_dict: result.employee_data_dict, is_in_group: result.is_in_group, });
            $('.systray_notification').html(template);
        } catch (error) { }
    },

    triggerRpcAndUpdateCount: function() {
        var self = this; rpc.query({ model: 'hr.employee', method: 'get_birthday_reminders' }).then(function(result) { self.updateBirthdayIcon(self.calculateUpcomingBirthdaysCount(result.employee_data_dict)); if (!result.is_in_group) { $('.priority-groups-div').remove(); } });
    },

    closeDropdown: function() { $('.o_MessagingMenu_dropdownMenu').hide(); },
});
SystrayMenu.Items.push(SystrayWidget);
export default SystrayWidget;
