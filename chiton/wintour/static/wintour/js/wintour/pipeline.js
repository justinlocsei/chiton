(function($, _) {

window.Wintour = window.Wintour || {};

var TEMPLATES = {};
var WEIGHT_BASE = 10;

/**
 * Render a template
 *
 * @param {string} id The ID of the template
 * @param {object} context The context for rendering
 * @returns {string} The rendered output
 */
function renderTemplate(id, context) {
    var template = TEMPLATES[id];
    if (!template) {
        template = _.template($('#' + id).html());
        TEMPLATES[id] = template;
    }

    return template(context);
};

/**
 * A visualizer for a recommendation pipeline
 *
 * @param {object} $root The jQuery-wrapped root element
 */
function PipelineVisualizer($root) {
    this.$el = $root;
    this.$results = $root.find('.js-pipeline-data');
    this.$form = $root.find('.js-pipeline-form');
    this.$takeSnapshot = $root.find('.js-pipeline-form-take-snapshot');

    this.$basicsFilter = $root.find('.js-pipeline-basics-filter');
    this.$basicsFilterInput = $root.find('.js-pipeline-basics-filter-input');
    this.$basicsFilterSelectAll = $root.find('.js-pipeline-basics-filter-select-all');
    this.$basicsFilterClearSelection = $root.find('.js-pipeline-basics-filter-clear-selection');
    this.$basicsFilterCutoff = $root.find('.js-pipeline-basics-filter-cutoff');

    this._state = {
        cutoff: null,
        filters: {},
        recommendations: null
    };

    this._readState();

    this._enableForm();
    this._enableFilters();
    this._enableSnapshots();
    this._enableHistory();
    this._enableDetails();

    this._observeScrolling();
}

PipelineVisualizer.prototype = {

    /**
     * Visualize the recommendations generated by the pipeline
     *
     * @param {object} recommendations The raw data for the recommendations
     */
    visualize: function(recommendations) {
        var state = this._state;

        if (recommendations) {
            this._state.recommendations = recommendations;
        } else if (this._state.recommendations) {
            recommendations = this._state.recommendations;
        } else {
            return;
        }

        var context = {};
        var basicSlugs = Object.keys(recommendations);
        var numBasics = basicSlugs.length;

        var basics = [];

        for (var i = 0; i < numBasics; i++) {
            var basicSlug = basicSlugs[i];
            var data = recommendations[basicSlug];

            if (!state.filters[basicSlug]) { continue; }

            var garments = [];
            var numGarments = data.garments.length;
            for (var j = 0; j < numGarments; j++) {
                if (j >= state.cutoff) { break; }

                var garment = data.garments[j];
                var weight = (garment.weight * WEIGHT_BASE).toFixed(1);
                weight = weight.replace(/\.0$/, '');

                garments.push(renderTemplate('pipeline-template-garment', {
                    brand: garment.garment.brand,
                    id: garment.garment.pk,
                    name: garment.garment.name,
                    weight: weight
                }));
            }

            var basic = data.basic;
            basics.push({
                garments: garments,
                name: basic.name,
                slug: basic.slug
            });
        }

        context.basics = _.sortBy(_.compact(basics), function(basic) {
            return basic.name;
        });

        var output = renderTemplate('pipeline-template-basics', context);
        this.$results.html(output);
    },

    /**
     * Recalculate and re-render recommendations when the form is submitted
     */
    _enableForm: function() {
        var that = this;
        var $el = this.$el;
        var $form = this.$form;

        var endpoint = $form.attr('action');

        $form.on('submit', function(e) {
            e.preventDefault();

            $el.addClass('is-loading');
            $.ajax({
                url: endpoint,
                method: 'GET',
                data: $form.serialize(),
                dataType: 'json',
                success: function(response) {
                    $el.removeClass('is-loading');
                    that.visualize(response);
                }
            });
        });
    },

    /**
     * Allow snapshots of the current form to be added to the history
     */
    _enableSnapshots: function() {
        var that = this;

        this.$takeSnapshot.on('click', function() {
            var state = that._serializeState();
            window.history.pushState(state.state, null, state.url);
        });
    },

    /**
     * Update the form based on the browser history
     */
    _enableHistory: function() {
        var that = this;

        var state = window.history.state;
        if (state) {
            this._restoreHistory(state);
        } else {
            var currentState = this._serializeState();
            window.history.replaceState(currentState.state, null, currentState.url);
        }

        window.onpopstate = function(e) {
            that._restoreHistory(e.state);
        };
    },

    /**
     * Restore the form to match a given history state
     *
     * @param {object} state A description of the form's state
     */
    _restoreHistory: function(state) {
        var values = state.reduce(function(previous, pair) {
            if (!previous[pair.name]) {
                previous[pair.name] = [pair.value];
            } else {
                previous[pair.name].push(pair.value);
            }
            return previous;
        }, {});

        var inputs = Object.keys(values).map(function(field) {
            var value = values[field];
            if (value.length === 1) {
                value = value[0];
            }

            return {
                name: field,
                value: value
            };
        });

        var $el = this.$el;
        inputs.forEach(function(input) {
            var $inputs = $el.find(':input[name="' + input.name + '"]');
            $inputs.val(input.value);
            $inputs.change();
        });

        this.$form.submit();
    },

    /**
     * Allow the basic filters to restrict the output
     */
    _enableFilters: function() {
        var that = this;
        var $inputs = this.$basicsFilterInput;

        this.$basicsFilter.on('submit', function(e) {
            e.preventDefault();
            that.visualize();
        });

        this.$basicsFilterClearSelection.on('click', function() {
            that._modifyAllFilterInputs(false);
        });

        this.$basicsFilterSelectAll.on('click', function() {
            that._modifyAllFilterInputs(true);
        });

        this.$basicsFilter.on('change', $inputs, function(e) {
            var $input = $(e.target);
            var basic = $input.val();
            var enabled = $input.prop('checked');

            that._state.filters[basic] = enabled;
            that.visualize();
        });

        this.$basicsFilterCutoff.on('change', function() {
            var $input = $(this);

            that._state.cutoff = $input.val();
            that.visualize();
        });
    },

    /**
     * Modify all filter inputs to be enabled or disabled
     *
     * @param {boolean} enabled Whether to enable or disabled the filters
     */
    _modifyAllFilterInputs: function(enabled) {
        var $inputs = this.$basicsFilterInput;
        $inputs.prop('checked', enabled);

        var state = this._state;
        Object.keys(state.filters).forEach(function(basicSlug) {
            state.filters[basicSlug] = enabled;
        });

        this.visualize();
    },

    /**
     * Read state information from the form
     */
    _readState: function() {
        var that = this;

        this.$basicsFilterInput.each(function() {
            var $input = $(this);
            var basic = $input.val();
            var enabled = $input.prop('checked');

            that._state.filters[basic] = enabled;
            that.visualize();
        });

        this._state.cutoff = this.$basicsFilterCutoff.val();
    },

    /**
     * Serialize the state of the visualizer as a plain object
     *
     * @returns {object}
     */
    _serializeState: function() {
        var state = this.$form.serializeArray();
        state.push({name: 'cutoff', value: this._state.cutoff});

        var basics = this._state.filters;
        Object.keys(basics).forEach(function(slug) {
            if (basics[slug]) {
                state.push({name: 'basic', value: slug});
            }
        });

        var pairs = state.map(function(pair) {
            return pair.name + '=' + encodeURIComponent(pair.value);
        });
        var query = pairs.join('&');

        return {
            state: state,
            url: '?' + query
        };
    },

    /**
     * Allow clicking on a garment to show its details
     */
    _enableDetails: function() {
        var that = this;

        this.$results.on('click', '.js-pipeline-garment', function(e) {
            var $garment = $(this);
            var $details = $garment.find('.js-pipeline-garment-details');
            var id = $garment.data('id');

            if ($(e.target).closest('.js-pipeline-garment-details').length) {
                return;
            }

            var $basic = $garment.parents('.js-pipeline-basic');
            var basicSlug = $basic.data('slug');

            var data = _.find(that._state.recommendations[basicSlug].garments, function(garment) {
                return garment.garment.pk === id;
            });

            if ($details.is(':empty')) {
                var details = renderTemplate('pipeline-template-garment-details', {
                    weights: data.explanations.weights,
                    urls: data.urls
                });
                $details.html(details);
                $garment.addClass('is-expanded');
            } else {
                $details.empty();
                $garment.removeClass('is-expanded');
            }
        });
    },

    /**
     * Register a scroll handler that changes the class on secondary elements
     */
    _observeScrolling: function() {
        var $el = this.$el;
        var $window = $(window);

        var inflection = Math.min(
            this.$form.offset().top,
            this.$basicsFilter.offset().top
        );
        var isPast = false;

        var handleScroll = _.throttle(function(e) {
            var scrollTop = $window.scrollTop();
            if (scrollTop < inflection && isPast) {
                $el.removeClass('is-scrolling');
                isPast = false;
            } else if (scrollTop >= inflection && !isPast) {
                $el.addClass('is-scrolling');
                isPast = true;
            }
        }, 125);

        $window.on('scroll', handleScroll);
    }

};

/**
 * Create a new pipeline
 *
 * @param {object} options Options for creating the pipeline
 * @param {object} options.recommendations Raw data describing pre-generated recommendations
 * @param {object,string} options.root The root DOM element for the visualizer
 * @returns {Pipeline}
 */
window.Wintour.pipeline = function pipeline(options) {
    var settings = $.extend({
        recommendations: null,
        root: null
    }, options || {});

    var pipeline = new PipelineVisualizer($(settings.root));
    if (settings.recommendations) {
        pipeline.visualize(settings.recommendations);
    }

    return pipeline;
};

})(window.jQuery, window._);
