FROM php:7.4
RUN apt-get update
RUN apt-get install zip -y
COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer
RUN composer create-project laravel/laravel frontend
WORKDIR frontend
RUN composer require phenx/php-svg-lib:0.4.0
RUN composer require dompdf/dompdf:v2.0.1
COPY web.php routes/web.php
RUN mkdir /uploads
RUN mkdir /uploads/v1
RUN mkdir /uploads/v1/user
EXPOSE 8000
CMD [ "php", "artisan", "serve", "--host", "0.0.0.0" ]