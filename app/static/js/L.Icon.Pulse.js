/*!
 * leaflet-extra-markers
 * Custom Markers for Leaflet JS based on Awesome Markers
 * Leaflet ExtraMarkers
 * https://github.com/coryasilva/Leaflet.ExtraMarkers/
 * @author coryasilva <https://github.com/coryasilva>
 * @version 1.0.9
 */

!function(e,r){"object"==typeof exports&&"undefined"!=typeof module?r(exports):"function"==typeof define&&define.amd?define(["exports"],r):r((e.leaflet=e.leaflet||{},e.leaflet["extra-markers"]={}))}(this,function(e){"use strict";var r=L.ExtraMarkers={};r.version=L.ExtraMarkers.version="1.0.8",r.Icon=L.ExtraMarkers.Icon=L.Icon.extend({options:{iconSize:[35,45],iconAnchor:[17,42],popupAnchor:[1,-32],shadowAnchor:[10,12],shadowSize:[36,16],className:"",prefix:"",extraClasses:"",shape:"circle",icon:"",innerHTML:"",markerColor:"red",svgBorderColor:"#fff",svgOpacity:1,iconColor:"#fff",number:"",svg:!1},initialize:function(e){e=L.Util.setOptions(this,e)},createIcon:function(){var e=document.createElement("div"),r=this.options;return r.icon&&(e.innerHTML=this._createInner()),r.innerHTML&&(e.innerHTML=r.innerHTML),r.bgPos&&(e.style.backgroundPosition=-r.bgPos.x+"px "+-r.bgPos.y+"px"),r.svg?this._setIconStyles(e,"svg"):this._setIconStyles(e,r.shape+"-"+r.markerColor),e},_createInner:function(){var e="",r="",t=this.options;if(t.iconColor&&(e="style='color: "+t.iconColor+"' "),t.number&&(r="number='"+t.number+"' "),t.svg){var s='<svg xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 69.529271 95.44922" style="fill:'+t.markerColor+";stroke:"+t.svgBorderColor+";fill-opacity:"+t.svgOpacity+';" height="100%" width="100%" version="1.1" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/"><g transform="translate(-139.52 -173.21)"><path d="m174.28 173.21c-19.199 0.00035-34.764 15.355-34.764 34.297 0.007 6.7035 1.5591 12.813 5.7461 18.854l0.0234 0.0371 28.979 42.262 28.754-42.107c3.1982-5.8558 5.9163-11.544 6.0275-19.045-0.0001-18.942-15.565-34.298-34.766-34.297z"/></g></svg>';return"square"===t.shape&&(s='<svg xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 69.457038 96.523441" style="fill:'+t.markerColor+";stroke:"+t.svgBorderColor+";fill-opacity:"+t.svgOpacity+';" height="100%" width="100%" version="1.1" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/"><g transform="translate(-545.27 -658.39)"><path d="m545.27 658.39v65.301h22.248l12.48 31.223 12.676-31.223h22.053v-65.301h-69.457z"/></g></svg>'),"star"===t.shape&&(s='<svg style="top:0; fill:'+t.markerColor+";stroke:"+t.svgBorderColor+";fill-opacity:"+t.svgOpacity+';" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.w3.org/2000/svg" height="100%" width="100%" version="1.1" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" viewBox="0 0 77.690999 101.4702"><g transform="translate(-101.15 -162.97)"><g transform="matrix(1 0 0 1.0165 -65.712 -150.28)"><path d="m205.97 308.16-11.561 11.561h-16.346v16.346l-11.197 11.197 11.197 11.197v15.83h15.744l11.615 33.693 11.467-33.568 0.125-0.125h16.346v-16.346l11.197-11.197-11.197-11.197v-15.83h-15.83l-11.561-11.561z"/></g></g></svg>'),"penta"===t.shape&&(s='<svg style="fill:'+t.markerColor+";stroke:"+t.svgBorderColor+";fill-opacity:"+t.svgOpacity+';"   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 71.550368 96.362438" height="100%" width="100%" version="1.1" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/"><g transform="translate(-367.08 -289.9)"><path d="m367.08 322.5 17.236-32.604h36.151l18.164 32.25-35.665 64.112z"/></g></svg>'),s+"<i "+r+e+"class='"+t.extraClasses+" "+t.prefix+" "+t.icon+"'></i>"}return"<i "+r+e+"class='"+t.extraClasses+" "+t.prefix+" "+t.icon+"'></i>"},_setIconStyles:function(e,r){var t,s,o=this.options,n=L.point(o["shadow"===r?"shadowSize":"iconSize"]);"shadow"===r?(t=L.point(o.shadowAnchor||o.iconAnchor),s="shadow"):(t=L.point(o.iconAnchor),s="icon"),!t&&n&&(t=n.divideBy(2,!0)),e.className="leaflet-marker-"+s+" extra-marker extra-marker-"+r+" "+o.className,t&&(e.style.marginLeft=-t.x+"px",e.style.marginTop=-t.y+"px"),n&&(e.style.width=n.x+"px",e.style.height=n.y+"px")},createShadow:function(){var e=document.createElement("div");return this._setIconStyles(e,"shadow"),e}}),r.icon=L.ExtraMarkers.icon=function(e){return new L.ExtraMarkers.Icon(e)},e.ExtraMarkers=r,Object.defineProperty(e,"__esModule",{value:!0})});

//TODO Tidy up

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

//MODIFIED

(function(window) {

    L.Icon.Pulse = L.DivIcon.extend({

        options: {
            className: '',
            iconSize: [12,12],
            fillColor: 'red',
            color: 'red',
            animate: true,
            heartbeat: 1,
            fontAwesomeIcon: null,
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

            this.options.className += ' leaflet-pulsing-icon ' +uniqueClassName;
            if (this.options.fontAwesomeIcon) {
                this.options.className += ' fas fa-1fourx fa-' + this.options.fontAwesomeIcon;
            }

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