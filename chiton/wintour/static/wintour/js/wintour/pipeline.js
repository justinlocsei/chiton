(function($, _) {

window.Wintour = window.Wintour || {};

// A map of template IDs to compiled template functions
var COMPILED_TEMPLATES = {};

// The maximum weight value to show
var WEIGHT_BASE = 10;

/**
 * Render a template
 *
 * @param {string} id The ID of the template
 * @param {object} context The context for rendering
 * @returns {string} The rendered output
 */
function renderTemplate(id, context) {
    var template = COMPILED_TEMPLATES[id];
    if (!template) {
        template = _.template($('#' + id).html());
        COMPILED_TEMPLATES[id] = template;
    }

    return template(context);
};

/**
 * A visualizer for a recommendation pipeline
 *
 * @param {object} $root The jQuery-wrapped root element
 * @param {boolean} hasData Whether the visualizer has data to show
 */
function PipelineVisualizer($root, hasData) {
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
    this._enableFormPinning();
    this._enableFilters();
    this._enableSnapshots();
    this._enableHistory(hasData);
    this._enableDetails();
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

        var basics = [];
        var context = {};
        var basicRecs = recommendations.basics || {};
        var basicSlugs = Object.keys(basicRecs);
        var numBasics = basicSlugs.length;

        // Build a context for rendering each basic and its garments, respecting
        // the current basic filters and the garment cutoff
        for (var i = 0; i < numBasics; i++) {
            var basicSlug = basicSlugs[i];
            var data = basicRecs[basicSlug];

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

        context.basics = _.sortBy(_.compact(basics), 'name');
        var output = renderTemplate('pipeline-template-basics', context);
        this.$results.html(output);

        var debug = recommendations.debug || {};
        var queries = debug.queries || [];
        var debugPanel = renderTemplate('pipeline-template-debug', {
            queries: queries.map(function(query) {
                return {
                    time: Math.round(parseFloat(query.time) * 1000),
                    sql: query.sql
                };
            }),
            queryCount: queries.length,
            time: Math.round(debug.time * 1000)
        });
        this.$results.append(debugPanel);
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
     * Update the form to match the current history state
     *
     * @params {boolean} updateState Whether to replace the current browser state
     */
    _enableHistory: function(updateState) {
        var that = this;

        if (!window.history.state && updateState) {
            var state = this._serializeState();
            window.history.replaceState(state.state, null, state.url);
        }

        window.onpopstate = function(e) {
            if (e.state) {
                that._restoreHistory(e.state);
            }
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
            if (value.length === 1) { value = value[0]; }

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
     * Allow the basic filter to restrict the output
     */
    _enableFilters: function() {
        var that = this;

        this.$basicsFilterClearSelection.on('click', function() { that._toggleBasicFilters(false); });
        this.$basicsFilterSelectAll.on('click', function() { that._toggleBasicFilters(true); });

        this.$basicsFilter.on('submit', function(e) {
            e.preventDefault();
            that.visualize();
        });

        this.$basicsFilter.on('change', this.$basicsFilterInput, function(e) {
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
    _toggleBasicFilters: function(enabled) {
        var $inputs = this.$basicsFilterInput;
        $inputs.prop('checked', enabled);

        var state = this._state;
        Object.keys(state.filters).forEach(function(basicSlug) {
            state.filters[basicSlug] = enabled;
        });

        this.visualize();
    },

    /**
     * Populate the state based on the current state of the form
     */
    _readState: function() {
        var that = this;

        this.$basicsFilterInput.each(function() {
            var $input = $(this);
            var basic = $input.val();

            that._state.filters[basic] = $input.prop('checked');
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

        return {
            state: state,
            url: '?' + pairs.join('&')
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

            var inDetails = $(e.target).closest('.js-pipeline-garment-details').length;
            if (inDetails) { return; }

            if (!$details.is(':empty')) {
                $details.empty();
                $garment.removeClass('is-expanded');
                return;
            }

            var $basic = $garment.parents('.js-pipeline-basic');
            var basicSlug = $basic.data('slug');

            // Get the recommendations data for the current garment from the
            // state, and create formatted objects to pass to the template
            var id = $garment.data('id');
            var data = _.find(
                that._state.recommendations.basics[basicSlug].garments,
                function(garment) { return garment.garment.pk === id; }
            );

            var weights = data.explanations.weights.reduce(function(previous, weight) {
                return previous.concat(weight.reasons.map(function(reason) {
                    return {
                        message: reason.reason,
                        weight: reason.weight,
                        weightName: weight.name
                    };
                }));
            }, []);

            var normalization = data.explanations.normalization.map(function(action) {
                return {
                    isNormalized: true,
                    message: action.action,
                    weight: action.weight,
                    weightName: action.name
                };
            });

            var allWeights = that._orderWeights(weights).concat(that._orderWeights(normalization));

            var links = Object.keys(data.urls).map(function(group) {
                return {
                    name: group,
                    links: data.urls[group]
                };
            });

            // Render the details and add them to the garment
            var details = renderTemplate('pipeline-template-garment-details', {
                weights: allWeights,
                links: _.sortBy(links, 'name')
            });
            $details.html(details);
            $garment.addClass('is-expanded');
        });
    },

    /**
     * Order a list of weight explanations by weight name and weight value
     *
     * @param {object[]} weights A list of weight explanations
     * @returns {object[]} The ordered weights
     */
    _orderWeights: function(weights) {
        return _.orderBy(weights, ['weightName', 'weight'], ['asc', 'desc']);
    },

    /**
     * Register a scroll handler that pins the form elements
     */
    _enableFormPinning: function() {
        var $el = this.$el;
        var $window = $(window);

        var inflection = Math.min(this.$form.offset().top, this.$basicsFilter.offset().top);
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
window.Wintour.pipeline = function(options) {
    var settings = $.extend({
        recommendations: {},
        root: null
    }, options || {});

    var basics = settings.recommendations.basics;
    var hasData = basics && !_.isEmpty(basics);

    var pipeline = new PipelineVisualizer($(settings.root), hasData);
    if (hasData) {
        pipeline.visualize(settings.recommendations);
    }

    return pipeline;
};

})(window.jQuery, window._);