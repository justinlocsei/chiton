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
    this._enableFormBatchControls();
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
        var numBasics = basicRecs.length;

        // Build a context for rendering each basic and its garments, respecting
        // the current basic filters and the garment cutoff
        for (var i = 0; i < numBasics; i++) {
            var data = basicRecs[i];
            if (!state.filters[data.basic.slug]) { continue; }

            // Build a lookup table mapping garment records to IDs
            var garmentsByID = data.garments.reduce(function(previous, garment) {
                previous[garment.garment.id] = garment;
                return previous;
            }, {});

            // Provide data on each price group that contains rendered garments
            var priceFacet = _.find(data.facets, function(facet) { return facet.slug === 'price'; });
            var priceGroups = priceFacet.groups.map(function(priceGroup) {
                var garments = [];
                var garmentIDs = priceGroup.garment_ids;
                var numGarments = Math.min(data.garments.length, garmentIDs.length);

                for (var j = 0; j < numGarments; j++) {
                    if (j >= state.cutoff) { break; }

                    var garment = garmentsByID[garmentIDs[j]];
                    var weight = (garment.weight * WEIGHT_BASE).toFixed(1);
                    weight = weight.replace(/\.0$/, '');

                    garments.push(renderTemplate('pipeline-template-garment', {
                        brand: garment.garment.brand,
                        editURL: garment.edit_url,
                        id: garment.garment.id,
                        name: garment.garment.name,
                        weight: weight
                    }));
                }

                return {
                    garments: garments,
                    name: priceGroup.slug
                };
            });

            var basic = data.basic;
            basics.push({
                name: basic.name,
                priceGroups: priceGroups,
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
     * Allow batch buttons to select all or none of a field group's options
     */
    _enableFormBatchControls: function() {
        var $buttons = this.$form.find('.js-pipeline-form-batch-button');

        $buttons.on('click', function(e) {
            var $button = $(e.target);
            var $field = $button.parents('.js-pipeline-form-fields');
            var $inputs = $field.find('input:checkbox');

            var isChecked = $button.data('query') === 'all';
            $inputs.prop('checked', isChecked);
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
        var $el = this.$el;

        var values = state.reduce(function(previous, pair) {
            if (!previous[pair.name]) {
                previous[pair.name] = [pair.value];
            } else {
                previous[pair.name].push(pair.value);
            }
            return previous;
        }, {});

        var inputs = Object.keys(values).map(function(field) {
            var $inputs = $el.find(':input[name="' + field + '"]');
            var value = values[field];
            if (value.length === 1 && !$inputs.length > 1) { value = value[0]; }

            return {
                name: field,
                value: value
            };
        });

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
        var $body = $('body');

        this.$results.on('click', '.js-pipeline-garment-meta', function(e) {
            var $meta = $(this);
            var $garment = $meta.parents('.js-pipeline-garment');
            var $details = $garment.find('.js-pipeline-garment-details');
            var $affiliates = $garment.find('.js-pipeline-garment-affiliates');
            var $priceGroup = $meta.parents('.js-pipeline-price-group');
            var $priceGroups = $meta.parents('.js-pipeline-price-groups');

            if (!$details.is(':empty')) {
                $affiliates.empty();
                $details.empty();
                $garment.removeClass('is-expanded');
                $priceGroup.removeClass('is-focused');
                $priceGroups.removeClass('is-active');
                return;
            }

            var $basic = $garment.parents('.js-pipeline-basic');
            var basicSlug = $basic.data('slug');

            // Get the recommendations data for the current garment from the
            // state, and create formatted objects to pass to the template
            var id = $garment.data('id');
            var basic = _.find(that._state.recommendations.basics, function(basic) {
                return basic.basic.slug === basicSlug;
            });
            var data = _.find(basic.garments, function(garment) {
                return garment.garment.id === id;
            });

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
                    importance: action.importance,
                    weight: action.weight,
                    weightName: action.name
                };
            });

            // Render the details and add them to the garment
            var details = renderTemplate('pipeline-template-garment-details', {
                weights: {
                    detailed: that._orderWeights(weights),
                    normalized: that._orderWeights(normalization)
                }
            });
            $details.html(details);
            $garment.addClass('is-expanded');
            $priceGroup.addClass('is-focused');
            $priceGroups.addClass('is-active');

            // Show all purchase options
            _.forEach(data.purchase_options, function(option) {
                var price;
                if (option.price) {
                    price = (option.price / 100).toFixed(2);
                    price = price.replace(/\.0+$/, '');
                }

                var images = _.sortBy(option.images, function(image) {
                    return image.height + image.width;
                });

                var affiliates = renderTemplate('pipeline-template-garment-affiliate', {
                    adminLinks: option.admin_links,
                    image: images[images.length - 1].url,
                    name: data.garment.name,
                    price: price,
                    retailer: option.retailer,
                    thumbnail: images[0].url,
                    url: option.url
                });
                $affiliates.append(affiliates);
            });
        });

        this.$results.on('click', '.js-pipeline-affiliate-image', function(e) {
            $body.addClass('is-modal');

            var $image = $(this);
            var modal = renderTemplate('pipeline-template-affiliate-image', {
                name: $image.attr('title'),
                url: $image.data('full')
            });
            var $modal = $(modal);
            $('body').append($modal);

            function close() {
                $modal.remove();
                $body.removeClass('is-modal');
                $body.off('keyup.affiliateImage');
            }

            $body.on('keyup.affiliateImage', function(e) { if (e.which === 27) { close(); } });
            $modal.find('.js-pipeline-affiliate-image-close').on('click', close);
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

        var inflection = this.$basicsFilter.offset().top;
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
