/*
The MIT License (MIT)

Copyright (c) 2015, Filip Zavadil
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

(function(window) {

    L.Icon.Pulse = L.DivIcon.extend({

        options: {
            className: '',
            iconSize: [12,12],
            fillColor: 'red',
            color: 'red',
            animate: true,
            heartbeat: 1,
        },

        initialize: function (options) {
            L.setOptions(this,options);

            // css

            var uniqueClassName = 'lpi-'+ new Date().getTime()+'-'+Math.round(Math.random()*100000);

            var before = ['background-color: '+this.options.fillColor];
            var after = [

                'box-shadow: 0 0 6px 2px '+this.options.color,

                'animation: pulsate ' + this.options.heartbeat + 's ease-out',
                'animation-iteration-count: infinite',
                'animation-delay: '+ (this.options.heartbeat + .1) + 's',
                'position:absolute',
                'left:0',
            ];

            if (!this.options.animate){
                after.push('animation: none');
                after.push('box-shadow:none');
            }

            var css = [
                '.'+uniqueClassName+'{'+before.join(';')+';}',
                '.'+uniqueClassName+':after{'+after.join(';')+';}',
            ].join('');

            var el = document.createElement('style');
            if (el.styleSheet){
                el.styleSheet.cssText = css;
            } else {
                el.appendChild(document.createTextNode(css));
            }

            document.getElementsByTagName('head')[0].appendChild(el);

            // apply css class

            this.options.className = this.options.className+' leaflet-pulsing-icon '+uniqueClassName;

            // initialize icon

            L.DivIcon.prototype.initialize.call(this, options);

        }
    });

    L.icon.pulse = function (options) {
        return new L.Icon.Pulse(options);
    };


    L.Marker.Pulse = L.Marker.extend({
        initialize: function (latlng,options) {
            options.icon = L.icon.pulse(options);
            L.Marker.prototype.initialize.call(this, latlng, options);
        }
    });

    L.marker.pulse = function (latlng,options) {
        return new L.Marker.Pulse(latlng,options);
    };

})(window);