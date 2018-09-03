(function(define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'backbone', 'edx-ui-toolkit/js/utils/string-utils',
        'edx-ui-toolkit/js/utils/html-utils', 'js/views/fields', 'backbone-super'
    ], function(gettext, $, _, Backbone, StringUtils, HtmlUtils, FieldViews) {
        var LearnerNotesFieldViews = {};

        LearnerNotesFieldViews.AccountPrivacyFieldView = FieldViews.DropdownFieldView.extend({

            render: function() {
                this._super();
                this.showNotificationMessage();
                this.updateFieldValue();
                return this;
            },

            showNotificationMessage: function() {
                var accountSettingsLink = HtmlUtils.joinHtml(
                    HtmlUtils.interpolateHtml(
                        HtmlUtils.HTML('<a href="{settings_url}">'), {settings_url: this.options.accountSettingsPageUrl}
                    ),
                    gettext('Account Settings page.'),
                    HtmlUtils.HTML('</a>')
                );
		this._super('');
            },

            updateFieldValue: function() {
		console.log('delete');
            }
        });

        return LearnerNotesFieldViews;
    });
}).call(this, define || RequireJS.define);
