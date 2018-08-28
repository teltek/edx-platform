(function(define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'backbone', 'edx-ui-toolkit/js/utils/html-utils',
        'common/js/components/views/tabbed_view',
        'js/student_profile/views/section_two_tab',
        'text!templates/learner_notes/learner_notes.underscore'],
        function(gettext, $, _, Backbone, HtmlUtils, TabbedView, SectionTwoTab, learnerNotesTemplate) {
            var LearnerNotesView = Backbone.View.extend({

                initialize: function(options) {
                    this.options = _.extend({}, options);
                    _.bindAll(this, 'showFullProfile', 'render', 'renderFields', 'showLoadingError');
                    var Router = Backbone.Router.extend({
                        routes: {':accomplishments': 'loadTab'}
                    });

                    this.router = new Router();
                    this.firstRender = true;
                },

                template: _.template(learnerNotesTemplate),

                showFullProfile: function() {
                    return true;
                },

                setActiveTab: function(tab) {
                // This tab may not actually exist.
                    if (this.tabbedView.getTabMeta(tab).tab) {
                        this.tabbedView.setActiveTab(tab);
                    }
                },

                render: function() {
                    var tabs,
                        self = this;

                    HtmlUtils.setHtml(this.$el, HtmlUtils.template(learnerNotesTemplate)({
                        username: self.options.accountSettingsModel.get('username'),
                        ownProfile: self.options.ownProfile,
                        showFullProfile: self.showFullProfile()
                    }));
                    this.renderFields();

                    if (this.showFullProfile() && (this.options.accountSettingsModel.get('accomplishments_shared'))) {
                        tabs = [
                            {
                                view: this.options.badgeListContainer,
                                title: gettext('Accomplishments'),
                                url: 'accomplishments'
                            }
                        ];

                        // Build the accomplishments Tab and fill with data
                        this.options.badgeListContainer.collection.fetch().done(function() {
                            self.options.badgeListContainer.render();
                        }).error(function() {
                            self.options.badgeListContainer.renderError();
                        });

                        this.tabbedView = new TabbedView({
                            tabs: tabs,
                            router: this.router,
                            viewLabel: gettext('Profile')
                        });

                        this.tabbedView.render();
                        this.$el.find('.account-settings-container').append(this.tabbedView.el);

                        if (this.firstRender) {
                            this.router.on('route:loadTab', _.bind(this.setActiveTab, this));
                            Backbone.history.start();
                            this.firstRender = false;
                            // Load from history.
                            this.router.navigate((Backbone.history.getFragment() || 'about_me'), {trigger: true});
                        } else {
                            // Restart the router so the tab will be brought up anew.
                            Backbone.history.stop();
                            Backbone.history.start();
                        }
                    }
                    return this;
                },

                renderFields: function() {
                    var view = this;
                },

                showLoadingError: function() {
                    this.$('.ui-loading-indicator').addClass('is-hidden');
                    this.$('.ui-loading-error').removeClass('is-hidden');
                }
            });

            return LearnerNotesView;
        });
}).call(this, define || RequireJS.define);
