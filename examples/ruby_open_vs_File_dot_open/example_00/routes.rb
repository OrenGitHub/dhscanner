Rails.application.routes.draw do

  get "/status", to: "vuln#get_handler"
  post "/vuln", to: "vuln#post_handler"

end
