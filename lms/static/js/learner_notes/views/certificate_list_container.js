(function(define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'common/js/components/views/paginated_view',
        'js/learner_notes/views/certificate_view', 'js/learner_notes/views/certificate_list_view',
        'text!templates/learner_notes/certificate_list.underscore'],
        function(gettext, $, _, PaginatedView, CertificateView, CertificateListView, CertificateListTemplate) {
            var CertificateListContainer = PaginatedView.extend({
                type: 'certificate',

                itemViewClass: CertificateView,

                listViewClass: CertificateListView,

                viewTemplate: CertificateListTemplate,

                isZeroIndexed: true,

                paginationLabel: gettext('Accomplishments Pagination'),

                initialize: function(options) {
                    CertificateListContainer.__super__.initialize.call(this, options);
                    this.listView.find_courses_url = options.find_courses_url;
                    this.listView.certificateMeta = options.certificateMeta;
                    this.listView.ownProfile = options.ownProfile;
                }
            });

            return CertificateListContainer;
        });
}).call(this, define || RequireJS.define);
