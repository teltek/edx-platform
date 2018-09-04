(function(define, undefined) {
    'use strict';
    define(['gettext', 'jquery', 'underscore', 'backbone', 'moment',
            'text!templates/learner_notes/certificate.underscore',
            'js/student_profile/views/share_modal_view'],
        function(gettext, $, _, Backbone, Moment, certificateTemplate, ShareModalView) {
            var CertificateView = Backbone.View.extend({
                initialize: function(options) {
                    this.options = _.extend({}, options);
                    this.context = _.extend(this.options.model.toJSON(), {
                        'created': new Moment(this.options.model.toJSON().created_date),
                        'ownProfile': options.ownProfile,
                        'certificateMeta': options.certificateMeta
                    });
                },
                attributes: {
                    'class': 'certificate-display'
                },
                template: _.template(certificateTemplate),
                render: function() {
                    this.$el.html(this.template(this.context));
                    this.shareButton = this.$el.find('.share-button');
                    return this;
                }
            });

            return CertificateView;
        });
}).call(this, define || RequireJS.define);
