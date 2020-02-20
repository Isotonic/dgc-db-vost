#!/bin/sh
for file in /usr/share/nginx/html/js/app.*.js;
do
  if [ ! -f $file.tmpl.js ]; then
    cp $file $file.tmpl.js
  fi

  envsubst '$VUE_APP_MAPBOX_API_KEY' < $file.tmpl.js > $file
done

gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b '0.0.0.0:5000' dgvost:app --daemon && \
sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf && \
nginx -g 'daemon off;'