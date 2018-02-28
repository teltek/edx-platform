// Backbone.js Application Collection: Certificate Program Line

define([
    'backbone',
    'js/certificates/models/programline'
],
function(Backbone, ProgramLine) {
    'use strict';
    var ProgramLineCollection = Backbone.Collection.extend({
        model: ProgramLine
    });
    return ProgramLineCollection;
});
