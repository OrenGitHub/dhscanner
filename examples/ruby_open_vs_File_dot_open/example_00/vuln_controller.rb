require "json"

class VulnController < ApplicationController

  def get_handler

    if File.file?('pwned') then

      render plain: "You've been pwned !\n"

    else

      render plain: "Everything seems fine\n"

    end

  end

  def post_handler

    # get the sent file entity
    source = params["source"]

    begin

      # read content
      # oops ... ruby newbie ... used `open` instead of `File.open`
      # should be: file = File.open(source.tempfile)
      file = open(source)
      content = file.read
      file.close

    rescue

      content = ""

    ensure

      # return content length -> works fine !
      render plain: ">> #{content.length()}\n"

    end

  end

end
