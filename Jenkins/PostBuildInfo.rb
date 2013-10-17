#!/usr/bin/env ruby

require "hipchat"
require "net/http"
require "json"
require "trollop"


def download_jenkins_json(build_url)
    uri = URI("#{build_url}api/json")
    json = Net::HTTP.get(uri)
    return json
end

def extract_commits_from_json(json)

    parsed_json = JSON.parse(json)
    
    commit_set = Array.new

    remote_url = ""
    parsed_json['actions'].each{|action|

        if action.class == Hash
            if action.keys.include? "remoteUrls"
                remote = action['remoteUrls'][0].split(":")[1]
                remote_url = "http://github.com/#{remote.sub(".git", "")}"
            end
        end

    }


    commit_string = ""
    parsed_json['changeSet']['items'].each{|item|

        commit_string.concat("<a href='#{remote_url}/commit/#{item['id']}'>#{item['id'][0..5]}</a>  #{item['author']['fullName']}: #{item['msg']}<br>\n")
    }

    header_string = "<a href='#{parsed_json['url']}'>#{parsed_json['fullDisplayName']}</a>"
    hipchat_color = 'yellow'
    build_result = parsed_json['result']
    puts build_result
    if  build_result == "SUCCESS"
        header_string.concat(" Succeeded")
        hipchat_color = 'green'
    elsif build_result == "FAILURE"
        header_string.concat(" Failed")
        hipchat_color = 'red'
    else
        header_string.concat(" #{build_result}")

    end

    message_string = "#{header_string} <br>\n #{commit_string}"

    return {:string => message_string, :hipchat_color => hipchat_color}
end

def post_message_to_hipchat(hipchat_api_key, hipchat_room, message, color)

    client = HipChat::Client.new(hipchat_api_key)
    client[hipchat_room].send("Jenkins Bot", message, :color => color, :notify => true)
end

opts = Trollop::options do
    opt :build_url, "Jenkins build url.", :type => :string
    opt :hipchat_api_key, "HipChat api key", :type => :string
    opt :hipchat_room, "HipChat room name to post to.", :type => :string
end


if __FILE__ == $0
    json = download_jenkins_json(opts[:build_url])
    message = extract_commits_from_json(json)
    post_message_to_hipchat(opts[:hipchat_api_key], opts[:hipchat_room], message[:string], message[:hipchat_color])
    
end
