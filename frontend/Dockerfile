FROM nginx:alpine

RUN apk add --no-cache gettext

WORKDIR /usr/share/nginx/html

COPY html/ html/
COPY static/ static/
COPY nginx.conf.template /etc/nginx/nginx.conf.template

EXPOSE 3001

CMD ["/bin/sh", "-c", "echo '🔸 Starting NGINX on port 3001...\nAccess on http://localhost:3001/html/main.html' && envsubst '${BACKEND_URL}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]
