(function(define, undefined) {
    'use strict';
    define([
        'gettext',
        'jquery',
        'underscore',
        'edx-ui-toolkit/js/utils/html-utils',
        'common/js/components/views/list',
        'js/learner_notes/views/certificate_view',
        'text!templates/learner_notes/certificate_placeholder.underscore'
    ],
        function(gettext, $, _, HtmlUtils, ListView, CertificateView, certificatePlaceholder) {
            var CertificateListView = ListView.extend({
                tagName: 'div',

                template: HtmlUtils.template(certificatePlaceholder),

                renderCollection: function() {
                    var self = this,
                        $row;

                    this.$el.empty();

                    // Split into two columns.
                    this.collection.each(function(certificate, index) {
                        if (index % 2 === 0) {
                            $row = $('<div class="row">');
                            this.$el.append($row);
                        }
                        var $item = new CertificateView({
                            model: certificate,
                            certificateMeta: this.certificateMeta,
                            ownProfile: this.ownProfile
                        }).render().el;

                        if ($row) {
                            $row.append($item);
                        }

                        this.itemViews.push($item);
                    }, this);
                    // Placeholder must always be at the end, and may need a new row.
                    if (!this.collection.hasNextPage()) {
                        // find_courses_url set by CertificateListContainer during initialization.
                        if (this.collection.length % 2 === 0) {
                            $row = $('<div class="row">');
                            this.$el.append($row);
                        }

                        if ($row) {
                            HtmlUtils.append(
                                $row,
                                this.template({find_courses_url: self.find_courses_url})
                            );
                        }
                    }
                    return this;
                }
            });

            return CertificateListView;
        });
}).call(this, define || RequireJS.define);
