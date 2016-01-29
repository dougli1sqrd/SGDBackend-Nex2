lock '3.4.0'

set :application, 'SGDBackend-NEX2'

set :repo_url, 'git@github.com:yeastgenome/SGDBackend-Nex2.git'
set :branch, ENV['BRANCH'] || $1 if `git branch` =~ /\* (\S+)\s/m
set :deploy_to, '/data/www/' + fetch(:application)

set :user, ask('Username', nil)
set :tmp_dir, "/home/#{fetch(:user)}/tmp"

set :default_stage, "dev"

set :keep_releases, 5
set :format, :pretty
set :log_level, :debug

namespace :deploy do
  after :finishing, :config
  after :finishing, :build
  after :finishing, :restart
end
