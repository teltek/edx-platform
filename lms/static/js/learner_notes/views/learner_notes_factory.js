(function(define, undefined) {
    'use strict';
    define([
        'gettext',
        'jquery',
        'underscore',
        'backbone',
        'logger',
        'edx-ui-toolkit/js/pagination/paging-collection',
        'js/student_account/models/user_account_model',
        'js/student_account/models/user_preferences_model',
        'js/views/fields',
        'js/learner_notes/views/learner_notes_fields',
        'js/learner_notes/views/learner_notes_views',
        'js/student_profile/models/badges_model',
        'js/student_profile/views/badge_list_container',
        'js/student_account/views/account_settings_fields',
        'js/views/message_banner',
        'string_utils'
    ], function(gettext, $, _, Backbone, Logger, PagingCollection, AccountSettingsModel, AccountPreferencesModel,
                 FieldsView, LearnerNotesFieldsView, LearnerNotesView, BadgeModel, BadgeListContainer,
                 AccountSettingsFieldViews, MessageBannerView) {
        return function(options) {
            var learnerNotesElement = $('.wrapper-profile');

            var accountSettingsModel = new AccountSettingsModel(
                _.extend(
                    options.account_settings_data,
                    {'default_public_account_fields': options.default_public_account_fields}
                ),
                {parse: true}
            );
            var AccountPreferencesModelWithDefaults = AccountPreferencesModel.extend({
                defaults: {
                    account_privacy: options.default_visibility
                }
            });
            var accountPreferencesModel = new AccountPreferencesModelWithDefaults(options.preferences_data);

            accountSettingsModel.url = options.accounts_api_url;
            accountPreferencesModel.url = options.preferences_api_url;

            var editable = options.own_profile ? 'toggle' : 'never';

            var messageView = new MessageBannerView({
                el: $('.message-banner')
            });

            var BadgeCollection = PagingCollection.extend({
                queryParams: {
                    currentPage: 'current_page'
                }
            });
            var badgeCollection = new BadgeCollection();
            badgeCollection.url = options.badges_api_url;

            var badgeListContainer = new BadgeListContainer({
                'attributes': {'class': 'badge-set-display'},
                'collection': badgeCollection,
                'find_courses_url': options.find_courses_url,
                'ownProfile': options.own_profile,
                'badgeMeta': {
                    'badges_logo': options.badges_logo,
                    'backpack_ui_img': options.backpack_ui_img,
                    'badges_icon': options.badges_icon
                }
            });

            var learnerNotesView = new LearnerNotesView({
                el: learnerNotesElement,
                ownProfile: options.own_profile,
                has_preferences_access: options.has_preferences_access,
                accountSettingsModel: accountSettingsModel,
                preferencesModel: accountPreferencesModel,
                badgeListContainer: badgeListContainer
            });

            var getProfileVisibility = function() {
                return 'all_users';
            };

            var showLearnerNotesView = function() {
                // Record that the profile page was viewed
                Logger.log('edx.user.settings.viewed', {
                    page: 'profile',
                    visibility: getProfileVisibility(),
                    user_id: options.profile_user_id
                });

                // Render the view for the first time
                learnerNotesView.render();
            };

            showLearnerNotesView();

            return {
                accountSettingsModel: accountSettingsModel,
                accountPreferencesModel: accountPreferencesModel,
                learnerNotesView: learnerNotesView,
                badgeListContainer: badgeListContainer
            };
        };
    });
}).call(this, define || RequireJS.define);
