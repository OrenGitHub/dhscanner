FROM ruby
RUN apt-get update
RUN apt-get install vim -y
RUN gem install rails
RUN rails new example_00 --api --skip-action-mailer --skip-active-record
WORKDIR example_00
COPY routes.rb config
COPY vuln_controller.rb app/controllers
EXPOSE 3000
CMD [ "rails", "server", "-b", "0.0.0.0" ]