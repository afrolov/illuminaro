(function () {

    // bind jQuery to $ only within this scope to avoid conflicts
    var $ = jQuery;
    var exports = window.Illuminaro = window.Illuminaro || {};

    function debounce(threshold, func) {
        var timerId = null;
        var self, args;
        return function () {
            self = this;
            args = arguments;
            if (timerId != null) {
                clearTimeout(timerId);
                timerId = null;
            }
            timerId = setTimeout(function () {
                timerId = null;
                func.apply(self, args);
            }, threshold);
        };
    }

    var IlluminaroApp = function () {
        this.$socket = null;

        // Cached input values
        this.$inputValues = {};

        // Output bindings;
        this.$bindings = {};

        // Cached values and erros
        this.$values = {};
        this.$errors = {};
    };

    (function () {
        // extend IlluminaroApp prototype

        this.connect = function (initialInput) {
            this.$socket = this.createSocket();
            this.$initialInput = initialInput;
            // merge values of existing input values and initial input
            $.extend(this.$inputValues, initialInput);
            //this.$updateConditionals();
        };

        this.isConnected = function () {
            return !!this.$socket;
        };

        this.createSocket = function () {
            var self = this;

            var ws = new WebSocket('ws://' + window.location.host + '/api');
            ws.binaryType = 'arraybuffer';

            ws.onopen = function () {
                // send initial data
                ws.send(JSON.stringify({
                    method: 'init',
                    data: self.$initialInput
                }));

                // send any pending data we have
                while (self.$pendingMessages && self.$pendingMessages.length) {
                    var message = self.$pendingMessages.shift();
                    ws.send(message);
                }
            };

            ws.onmessage = function (e) {
                self.dispatchMessage(e.data);
            };

            ws.onclose = function () {
                $(document.body).addClass('disconnected');
            };

            return ws;
        };

        this.sendInput = function (values) {
            var message = JSON.stringify({
                method: 'update',
                data: values
            });

            this.$sendMessage(message);
        };

        this.$sendMessage = function (message) {
            //if (!this.$socket.readyState) { // TODO fixme readyState
            //    this.$pendingMessages.push(message);
            //} else {
            this.$socket.send(message);
            //}
        };

        this.receiveOutput = function (name, value) {
            if (this.$values[name] === value) {
                // do not do anything if we already have that value
                return '';
            }

            // set value
            this.$values[name] = value;
            // clear error state
            delete this.$errors[name];

            // invoke associated binding
            var binding = this.$bindings[name];
            if (binding) {
                binding.onValueChange(value);
            }

            return value;
        };

        this.dispatchMessage = function (message) {
            var messageObject = JSON.parse(message);
            console.log("client: got message: " + message);

            // turn off all possible "pending update" indicators
            if (messageObject.values) {
                var value_name;
                for (value_name in this.$bindings) {
                    this.$bindings[value_name].showProgress(false);
                }
            }

            // set error indicators
            var key;
            for (key in messageObject.errors) {
                this.receiveError(key, messageObject.errors[key]);
            }

            // distribute values to widgets
            for (key in messageObject.values) {
                this.receiveOutput(key, messageObject.values[key]);
            }

            // print console messages from the server
            if (messageObject.console) {
                for (var i = 0; i < messageObject.console.length; i++) {
                    console.log(messageObject.console[i]);
                }
            }

            // update progress indicators if any
            // TODO: possibly numerical values for percentage complete, ETA etc
            if (messageObject.progress) {
                for (i = 0; i < messageObject.progress.length; i++) {
                    key = messageObject.progress[i];
                    var binding = this.$bindings[key];
                    if (binding && binding.showProgress) {
                        binding.showProgress(true);
                    }
                }
            }

            // TODO update request object with the response status
        };

        this.bindOutput = function (id, binding) {
            if (!id) {
                throw "Cannot find an element with no ID";
            }

            if (this.$bindings[id]) {
                throw "Duplicate binding for ID: " + id;
            }
            this.$bindings[id] = binding;
        };

        this.unbindOutput = function (id, binding) {
            if (this.$bindings[id] === binding) {
                delete this.$bindings[id];
                return true;
            } else {
                return false;
            }
        };

        this.$updateConditionals = function () {
            // TODO implement conditional widgets
        };

    }).call(IlluminaroApp.prototype);

    // TODO
    // * FileProcessor

    var BindingRegistry = function () {
        this.bindings = [];
        this.bindingNames = {};
    };

    (function () {
        this.register = function (binding, bindingName, priority) {
            var bindingObject = { binding: binding, priority: priority };
            // add new binding to the beginning of the array
            this.bindings.unshift(bindingObject);
            if (bindingName) {
                this.bindingNames[bindingName] = bindingObject;
                binding.name = bindingName;
            }
        };

        // TODO setPriority/getPriority methods

        this.getBindings = function () {
            // TODO sort by priority
            return this.bindings;
        };

    }).call(BindingRegistry.prototype);

    var inputBindings = exports.inputBindings = new BindingRegistry();
    var outputBindings = exports.outputBindings = new BindingRegistry();

    var OutputBinding = exports.OutputBinding = function () {
    };

    (function () {
        this.find = function (scope) {
            throw "Not implemented";
        };

        this.getId = function (el) {
            return $(el).attr('data-input-id') || el.id;
        };

        this.onValueChange = function (el, data) {
            this.clearError(el);
            this.renderValue(el, data);
        };

        this.onValueError = function (el, err) {
            this.renderError(el, err);
        };

        this.renderError = function (el, err) {
            $(el).addClass('illuminaro-output-error').text(err.message);
        };

        this.clearError = function (el) {
            $(el).removeClass('illuminaro-output-error');
        };

        this.showProgress = function (el, show) {
            var recalculation_class = 'recalculating';
            if (show)
                $(el).addClass(recalculation_class);
            else
                $(el).removeClass(recalculation_class);
        };

    }).call(OutputBinding.prototype);


    var textOutputBinding = new OutputBinding();
    $.extend(textOutputBinding, {
        find: function (scope) {
            return $(scope).find('.illuminaro-text-output');
        },
        renderValue: function (el, data) {
            $(el).text(data);
        }
    });
    outputBindings.register(textOutputBinding, 'illuminaro.textOutput');

    var plotOutputBinding = new OutputBinding();
    $.extend(plotOutputBinding, {
        find: function (scope) {
            return $(scope).find('.illuminaro-plot-output');
        },
        renderValue: function (el, data) {
            // Load the image before emptying, to minimize flicker
            var img = null;
            if (data) {
                img = document.createElement('img');
                img.src = data;
            }

            $(el).empty();
            if (img)
                $(el).append(img);
        }
    });
    outputBindings.register(plotOutputBinding, 'illuminaro.plotOutput');

    var htmlOutputBinding = new OutputBinding();
    $.extend(htmlOutputBinding, {
        find: function (scope) {
            return $(scope).find('.illuminaro-html-output');
        },
        renderValue: function (el, data) {
            exports.unbindAll(el);
            $(el).html(data);
            exports.bindAll(el);
        }
    });
    outputBindings.register(htmlOutputBinding, 'illuminaro.htmlOutput');


    var InputBinding = exports.InputBinding = function () {
    };

    (function () {
        this.find = function (scope) {
            throw "Not implemented";
        };

        this.getId = function (el) {
            return $(el).attr('data-input-id') || el.id;
        };

        this.getType = function () {
            return false;
        };

        this.getValue = function (el) {
            throw "Not implemented";
        };

        this.subscribe = function (el, callback) {
            // empty
        };

        this.unsubscribe = function (el) {
            // empty
        };

        this.getRatePolicy = function () {
            return null;
        };

    }).call(InputBinding.prototype);

    // Text input
    var textInputBinding = new InputBinding();
    $.extend(textInputBinding, {
        find: function (scope) {
            return $(scope).find('input[type="text"]');
        },
        getId: function (el) {
            return InputBinding.prototype.getId.call(this, el) || el.name;
        },
        getValue: function (el) {
            return el.value;
        },
        setValue: function (el, value) {
            el.value = value;
        },
        subscribe: function (el, callback) {
            $(el).on('keyup.textInputBinding input.textInputBinding', function (event) {
                callback(true);
            });
            $(el).on('change.textInputBinding', function (event) {
                callback(false);
            });
        },
        unsubscribe: function (el) {
            $(el).off('.textInputBinding');
        },
        getRatePolicy: function () {
            return {
                policy: 'debounce',
                delay: 250
            };
        }
    });
    inputBindings.register(textInputBinding, 'illuminaro.textInput');


    var textareaInputBinding = {};
    $.extend(textareaInputBinding, textInputBinding, {
        find: function (scope) {
            return $(scope).find('textarea');
        }
    });
    inputBindings.register(textareaInputBinding, 'illuminaro.textareaInput');


    var numberInputBinding = {};
    $.extend(numberInputBinding, textInputBinding, {
        find: function (scope) {
            return $(scope).find('input[type="number"]');
        },
        getValue: function (el) {
            var numberVal = $(el).val();
            if (!isNaN(numberVal))
                return +numberVal;
            else
                return numberVal;
        }
    });
    inputBindings.register(numberInputBinding, 'illuminaro.numberInput');

    // Bind to HTML5 plain slider (range input)
    var rangeInputBinding = {};
    $.extend(rangeInputBinding, numberInputBinding, {
        find: function (scope) {
            return $(scope).find('input[type=range]');
        },
        getValue: function (el) {
            return $(el).val();
        }
    });
    inputBindings.register(rangeInputBinding, 'illuminaro.rangeInput');

    // For future fancy jslider binding, dormant for now
    var jsliderInputBinding = {};
    $.extend(jsliderInputBinding, numberInputBinding, {
        find: function (scope) {
            // Check if jslider plugin is loaded
            if (!$.fn.slider)
                return [];

            var sliders = $(scope).find('input.jslider');
            sliders.slider();
            return sliders;
        },
        getValue: function (el) {
            var sliderVal = $(el).val();
            if (/;/.test(sliderVal)) {
                var chunks = sliderVal.split(/;/, 2);
                return [+chunks[0], +chunks[1]];
            }
            else {
                return +sliderVal;
            }
        },
        setValue: function (el, val) {
            // TODO: implement
        },
        subscribe: function (el, callback) {
            $(el).on('change.inputBinding', function (event) {
                callback(!$(el).data('animating'));
            });
        },
        unsubscribe: function (el) {
            $(el).off('.inputBinding');
        },
        getRatePolicy: function () {
            return {
                policy: 'debounce',
                delay: 250
            };
        }
    });
    inputBindings.register(jsliderInputBinding, 'illuminaro.jsliderInput');


    // Select input
    var selectInputBinding = new InputBinding();
    $.extend(selectInputBinding, {
        find: function (scope) {
            return scope.find('select');
        },
        getId: function (el) {
            return InputBinding.prototype.getId.call(this, el) || el.name;
        },
        getValue: function (el) {
            return $(el).val();
        },
        setValue: function (el, value) {
            $(el).val(value);
        },
        subscribe: function (el, callback) {
            $(el).on('change.selectInputBinding', function (event) {
                callback();
            });
        },
        unsubscribe: function (el) {
            $(el).off('.selectInputBinding');
        }
    });
    inputBindings.register(selectInputBinding, 'illuminaro.selectInput');

    // Toggle buttons
    var toggleButtonsInputBinding = new InputBinding();
    $.extend(toggleButtonsInputBinding, {
            find: function (scope) {
                return scope.find('.illuminaro-btn-group[data-toggle="illuminaro-buttons-checkbox"]');
            },
            getId: function (el) {
                return InputBinding.prototype.getId.call(this, el) || el.name;
            },
            getValue: function (el) {
                var result = $(el).children('.active').map(function () {
                    return $(this).text()
                });
                result = result.get();
                return result;
            },
            setValue: function (el) {
                // TODO FIXME
            },
            subscribe: function (el, callback) {
                $(el).children('.illuminaro-btn').on('click.toggleButtonsInputBinding', function (event) {
                    if (event.type == 'click') {
                        $(event.target).toggleClass('active');
                    }
                    callback();
                })
            },
            unsubscribe: function (el) {
                $(el).children('.illuminaro-btn').off('.toggleButtonsInputBinding');
            }
        }
    );
    inputBindings.register(toggleButtonsInputBinding, 'illuminaro.toggleButtons');

    // Toggle buttons
    var radioButtonsInputBinding = new InputBinding();
    $.extend(radioButtonsInputBinding, {
            find: function (scope) {
                return scope.find('.illuminaro-btn-group[data-toggle="illuminaro-buttons-radio"]');
            },
            getId: function (el) {
                return InputBinding.prototype.getId.call(this, el) || el.name;
            },
            getValue: function (el) {
                var result = $(el).children('.active').map(function () {
                    return $(this).text()
                });
                result = result.get();
		// unlike radio button, there can be only one value toggled, return
		// one element
                return result[0];
            },
            setValue: function (el) {
                // TODO FIXME
            },
            subscribe: function (el, callback) {
                $(el).children('.illuminaro-btn').on('click.radioButtonsInputBinding', function (event) {
                    if (event.type == 'click') {
                        $(el).children('.illuminaro-btn').removeClass('active');
                        $(event.target).toggleClass('active');
                    }
                    callback();
                })
            },
            unsubscribe: function (el) {
                $(el).children('.illuminaro-btn').off('.radioButtonsInputBinding');
            }
        }
    );
    inputBindings.register(radioButtonsInputBinding, 'illuminaro.radioButtons');


    var bootstrapTabInputBinding = new InputBinding();
    $.extend(bootstrapTabInputBinding, {
        find: function (scope) {
            return scope.find('ul.nav.nav-tabs');
        },
        getValue: function (el) {
            var anchor = $(el).children('li.active').children('a');
            if (anchor.length == 1)
                return this.$getTabName(anchor);
            return null;
        },
        setValue: function (el, value) {
            var self = this;
            var anchors = $(el).children('li').children('a');
            anchors.each(function () {
                if (self.$getTabName($(this)) === value) {
                    $(this).tab('show');
                    return false;
                }
            });
        },
        subscribe: function (el, callback) {
            $(el).on('shown.bootstrapTabInputBinding', function (event) {
                callback();
            });
        },
        unsubscribe: function (el) {
            $(el).off('.bootstrapTabInputBinding');
        },
        $getTabName: function (anchor) {
            return anchor.attr('data-value') || anchor.text();
        }
    });
    inputBindings.register(bootstrapTabInputBinding, 'illuminaro.bootstrapTabInput');

    // TODO file upload

    var OutputBindingAdapter = function (el, binding) {
        this.el = el;
        this.binding = binding;
    };

    (function () {
        this.onValueChange = function (data) {
            this.binding.onValueChange(this.el, data);
        };
        this.onValueError = function (err) {
            this.binding.onValueError(this.el, err);
        };
        this.showProgress = function (show) {
            this.binding.showProgress(this.el, show);
        };
    }).call(OutputBindingAdapter.prototype);

    // Immediately sends data to illuminaroapp
    var InputSender = function (illuminaroapp) {
        this.illuminaroapp = illuminaroapp;
    };
    (function () {
        this.setInput = function (name, value) {
            var data = {};
            data[name] = value;
            this.illuminaroapp.sendInput(data);
        };
    }).call(InputSender.prototype);

    function initIlluminaro() {

        var illuminaroapp = exports.illuminaroapp = new IlluminaroApp();

        function bindOutputs(scope) {

            if (scope == undefined)
                scope = document;

            scope = $(scope);

            var bindings = outputBindings.getBindings();

            for (var i = 0; i < bindings.length; i++) {
                var binding = bindings[i].binding;
                var matches = binding.find(scope) || [];
                for (var j = 0; j < matches.length; j++) {
                    var el = matches[j];
                    var id = binding.getId(el);

                    // Check if element has no ID
                    if (!id)
                        continue;

                    var bindingAdapter = new OutputBindingAdapter(el, binding);
                    illuminaroapp.bindOutput(id, bindingAdapter);
                    $(el).data('illuminaro-output-binding', bindingAdapter);
                    $(el).addClass('illuminaro-bound-output');
                }
            }

            // Send later in case DOM layout isn't final yet.
            setTimeout(sendPlotSize, 0);
        }

        function unbindOutputs(scope) {
            if (scope == undefined)
                scope = document;

            var outputs = $(scope).find('.illuminaro-bound-output');
            for (var i = 0; i < outputs.length; i++) {
                var bindingAdapter = $(outputs[i]).data('illuminaro-output-binding');
                if (!bindingAdapter)
                    continue;
                var id = bindingAdapter.binding.getId(outputs[i]);
                illuminaroapp.unbindOutput(id, bindingAdapter);
                $(outputs[i]).removeClass('illuminaro-bound-output');
            }
        }

        function elementToValue(el) {
            if (el.type == 'checkbox' || el.type == 'radio')
                return el.checked ? true : false;
            else
                return $(el).val();
        }

        //var inputs = new InputNoResendDecorator(new InputBatchSender(illuminaroapp));
        //var inputsRate = new InputRateDecorator(inputs);
        //var inputsDefer = new InputDeferDecorator(inputs);

        // TODO deferred and throttled inputs
        var inputs = new InputSender(illuminaroapp);
        var inputsRate = inputs;
        var inputsDefer = inputs;

        inputs = inputsRate;
        $('input[type="submit"], button[type="submit"]').each(function () {
            inputs = inputsDefer;
            $(this).click(function (event) {
                event.preventDefault();
                inputsDefer.submit();
            });
        });

        exports.onInputChange = function (name, value) {
            inputs.setInput(name, value);
        };

        var boundInputs = {};

        function valueChangeCallback(binding, el, allowDeferred) {
            var id = binding.getId(el);
            if (id) {
                var value = binding.getValue(el);
                var type = binding.getType(value);
                if (type)
                    id = id + ":" + type;
                inputs.setInput(id, value, !allowDeferred);
            }
        }

        function bindInputs(scope) {

            if (scope == undefined)
                scope = document;

            scope = $(scope);

            var bindings = inputBindings.getBindings();

            var currentValues = {};

            for (var i = 0; i < bindings.length; i++) {
                var binding = bindings[i].binding;
                var matches = binding.find(scope) || [];
                for (var j = 0; j < matches.length; j++) {
                    var el = matches[j];
                    var id = binding.getId(el);

                    // Check if ID is empty, or if already bound
                    if (!id || boundInputs[id])
                        continue;

                    var type = binding.getType(el);
                    var effectiveId = type ? id + ":" + type : id;
                    currentValues[effectiveId] = binding.getValue(el);

                    var thisCallback = (function () {
                        var thisBinding = binding;
                        var thisEl = el;
                        return function (allowDeferred) {
                            valueChangeCallback(thisBinding, thisEl, allowDeferred);
                        };
                    })();

                    binding.subscribe(el, thisCallback);
                    $(el).data('illuminaro-input-binding', binding);
                    $(el).addClass('illuminaro-bound-input');

                    // TODO fixme
                    //var ratePolicy = binding.getRatePolicy();
                    //if (ratePolicy != null) {
                    //    inputsRate.setRatePolicy(
                    //        id,
                    //        ratePolicy.policy,
                    //        ratePolicy.delay);
                    //}

                    boundInputs[id] = {
                        binding: binding,
                        node: el
                    };

                    if (illuminaroapp.isConnected()) {
                        valueChangeCallback(binding, el, false);
                    }
                }
            }

            return currentValues;
        }

        function unbindInputs(scope) {
            if (scope == undefined)
                scope = document;

            var inputs = $(scope).find('.illuminaro-bound-input');
            for (var i = 0; i < inputs.length; i++) {
                var binding = $(inputs[i]).data('illuminaro-input-binding');
                if (!binding)
                    continue;
                var id = binding.getId(inputs[i]);
                $(inputs[i]).removeClass('illuminaro-bound-input');
                delete boundInputs[id];
                binding.unsubscribe(inputs[i]);
            }
        }


        function getMultiValue(input, exclusiveValue) {
            if (!input.name)
                return null;

            els = $(
                'input:checked' +
                    '[type="' + input.type + '"]' +
                    '[name="' + input.name + '"]');
            var values = els.map(function () {
                return this.value;
            }).get();
            if (exclusiveValue) {
                if (values.length > 0)
                    return values[0];
                else
                    return null;
            }
            else {
                return values;
            }
        }

        function bindMultiInput(selector, exclusiveValue) {
            $(document).on('change input', selector, function () {
                if (this.name) {
                    inputs.setInput(this.name, getMultiValue(this, exclusiveValue));
                }
                if (!exclusiveValue) {
                    var id = this['data-input-id'] || this.id;
                    if (id) {
                        inputs.setInput(id, elementToValue(this));
                    }
                }
            });
        }

        function getMultiInputValues(scope, selector, exclusiveValue) {
            var initialValues = {};
            $(scope).find(selector).each(function () {
                if (this.name) {
                    initialValues[this.name] = getMultiValue(this, exclusiveValue);
                }
                if (!exclusiveValue) {
                    var id = this['data-input-id'] || this.id;
                    if (id) {
                        initialValues[id] = elementToValue(this);
                    }
                }
            });
            return initialValues;
        }

        function _bindAll(scope) {
            bindOutputs(scope);
            return $.extend(
                {},
                getMultiInputValues(scope, 'input[type="checkbox"]', false),
                getMultiInputValues(scope, 'input[type="radio"]', true),
                bindInputs(scope)
            );
        }

        function unbindAll(scope) {
            unbindInputs(scope);
            unbindOutputs(scope);
        }

        exports.bindAll = function (scope) {
            // _bindAll alone returns initial values, it doesn't send them to the
            // server. export.bindAll needs to send the values to the server, so we
            // wrap _bindAll in a closure that does that.
            var currentValues = _bindAll(scope);
            $.each(currentValues, function (name, value) {
                inputs.setInput(name, value);
            });
        };
        exports.unbindAll = unbindAll;

        bindMultiInput('input[type="checkbox"]', false);
        bindMultiInput('input[type="radio"]', true);
        var initialValues = _bindAll(document);


        // The server needs to know the size of each plot output element, in case
        // the plot is auto-sizing
        $('.illuminaro-plot-output').each(function () {
            var width = this.offsetWidth;
            var height = this.offsetHeight;
            initialValues['illuminaroout_' + this.id + '_width'] = width;
            initialValues['illuminaroout_' + this.id + '_height'] = height;
        });
        function sendPlotSize() {
            $('.illuminaro-plot-output').each(function () {
                inputs.setInput('illuminaroout_' + this.id + '_width', this.offsetWidth);
                inputs.setInput('illuminaroout_' + this.id + '_height', this.offsetHeight);
            });
        }

        // Various component initialization
        $('.illuminaro-datepicker').datepicker();

        // The size of each plot may change either because the browser window was
        // resized, or because a tab was shown/hidden (hidden elements report size
        // of 0x0). It's OK to over-report sizes because the input pipeline will
        // filter out values that haven't changed.
        $(window).resize(debounce(500, sendPlotSize));
        $('body').on('shown.sendPlotSize hidden.sendPlotSize', '*', sendPlotSize);

        // We've collected all the initial values--start the server process!
        illuminaroapp.connect(initialValues);
    } // function initIlluminaro()

    $(function () {
        // Init Illuminaro a little later than document ready, so user code can
        // run first (i.e. to register bindings)
        setTimeout(initIlluminaro, 1);
    });


})();
