#!/usr/bin/env ruby
# A local Liquid preview; GitHub Pages performs the production Jekyll build.
require 'fileutils'
require 'json'
require 'liquid'
require 'optparse'
require 'yaml'

options = { source: File.expand_path('..', __dir__) }
OptionParser.new do |parser|
  parser.on('--source DIR') { |path| options[:source] = File.expand_path(path) }
  parser.on('--output-dir DIR') { |path| options[:output] = File.expand_path(path) }
end.parse!
abort 'Provide --output-dir with a preview directory.' unless options[:output]
source = options[:source]
destination = File.join(options[:output], 'personal-website-router')
abort 'The preview must not overwrite the source checkout.' if destination == source

module RouterPreviewFilters
  def jsonify(value)
    JSON.generate(value)
  end
end
Liquid::Template.register_filter(RouterPreviewFilters)
site = YAML.safe_load(File.read(File.join(source, '_config.yml')))
rendered = {}
%w[index.html robots.txt sitemap.xml].each do |name|
  pieces = File.read(File.join(source, name)).split(/^---\s*$\n?/, 3)
  abort "Missing front matter in #{name}" unless pieces.length == 3
  template = Liquid::Template.parse(pieces[2], error_mode: :strict)
  rendered[name] = template.render!(
    { 'page' => YAML.safe_load(pieces[1]), 'site' => site },
    strict_variables: true, strict_filters: true
  )
end
FileUtils.mkdir_p(destination)
rendered.each { |name, content| File.write(File.join(destination, name), content) }
FileUtils.cp(File.join(source, 'personal-website-router-qr.png'), destination)
File.write(File.join(options[:output], 'start.html'),
           '<!doctype html><title>Router test start</title><a href="/personal-website-router/">Open router</a>')
puts "Rendered preview: #{destination}"
