# Credit to Michael Herman
# https://testdriven.io/blog/deploying-flask-to-heroku-with-docker-and-gitlab/#docker

# Build
FROM node:13.5.0 as build-vue
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend .
RUN npm run build

# Production
FROM nginx:stable-alpine as production
WORKDIR /app
RUN apk update && apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev jpeg-dev zlib-dev
COPY --from=build-vue /app/dist /usr/share/nginx/html
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ./backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY ./backend .
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
CMD [ "/entrypoint.sh" ]