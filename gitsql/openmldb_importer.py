#!/usr/bin/env python3

import logging
import openmldb.dbapi
from git import Repo

class OpenmldbImporter(object):

  def __init__(self, zk, zk_path, repo_dir):
    self.zk = zk
    self.zk_path = zk_path
    logging.info("Try to import the repo from {}".format(repo_dir))

    try:
      self.repo = Repo(repo_dir)
    except:
      logging.fatal("Fail to import git repo for path: {}".format(repo_dir))
      exit(-1)

    if self.repo.bare:
      logging.fatal("Git repo is bare, exit now")
      exit(-1)

    # Parse to get repo name
    repo_name = self.repo.git_dir.split("/")[-2]

    logging.info("Try to connect OpenMLDB for zk: {} and path: {}".format(zk, zk_path))
    # Use repo name as database name
    self.db_name = repo_name
    connection = openmldb.dbapi.connect(self.db_name, zk, zk_path)
    self.cursor = connection.cursor()


  def create_db_and_tables(self):
    logging.info("Try to create database {}".format(self.db_name))
    self.cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(self.db_name))

    logging.info("Try to create commit table")
    self.cursor.execute("CREATE TABLE commit (hexsha string, author string, email string, date int64, summary string,, size int, insertions int, deletions int, lines int, files int)")

    logging.info("Try to create branch table")
    self.cursor.execute("CREATE TABLE branch (name string, path string, commit string, remote bool, valid bool)")

    logging.info("Try to create tag table")
    self.cursor.execute("CREATE TABLE tag (name string, commit string)")

    logging.info("Success to create database and tables")


  def drop_db_and_tables(self):
    table_name = "commit"
    logging.info("Try to drop table {}".format(table_name))
    self.cursor.execute("DROP TABLE {}".format(table_name))

    table_name = "branch"
    logging.info("Try to drop table {}".format(table_name))
    self.cursor.execute("DROP TABLE {}".format(table_name))

    table_name = "tag"
    logging.info("Try to drop table {}".format(table_name))
    self.cursor.execute("DROP TABLE {}".format(table_name))

    logging.info("Success to delete database and tables")


  def insert_commit_row(self, commit):
    sql = """INSERT INTO commit VALUES ("{}", "{}", "{}", {}, "{}", {}, {}, {}, {}, {})""".format(
      commit.hexsha,
      # TODO(tobe): Use prepared statement
      commit.author.name.replace('"', '\\"'),
      commit.author.email.replace('"', '\\"'),
      commit.committed_date,
      commit.summary.replace('"', '\\"'),
      commit.size,
      commit.stats.total["insertions"],
      commit.stats.total["deletions"],
      commit.stats.total["lines"],
      commit.stats.total["files"]
    )
    try:
      self.cursor.execute(sql)
    except Exception as e:
      logging.error("Fail to execute sql: {}, get error: {}".format(sql, e))


  def insert_branch_row(self, branch):
    sql = """INSERT INTO branch VALUES ("{}", "{}", "{}", {}, {})""".format(
      branch.name,
      branch.path,
      branch.commit.hexsha,
      branch.is_remote(),
      branch.is_valid()
    )

    try:
      self.cursor.execute(sql)
    except Exception as e:
      logging.error("Fail to execute sql: {}, get error: {}".format(sql, e))


  def insert_tag_row(self, tag):
    sql = """INSERT INTO tag VALUES ("{}", "{}")""".format(
      tag.name,
      tag.commit
    )

    try:
      self.cursor.execute(sql)
    except Exception as e:
      logging.error("Fail to execute sql: {}, get error: {}".format(sql, e))


  def import_commit_data(self):
    num = 0
    for commit in self.repo.iter_commits():
      num += 1
      self.insert_commit_row(commit)
    logging.info("Total commit number: " + str(num))


  def import_branch_data(self):
    num = 0
    for branch in self.repo.branches:
      num += 1
      self.insert_branch_row(branch)
    logging.info("Total branch number: " + str(num))


  def import_tag_data(self):
    num = 0
    for tag in self.repo.tags:
      num += 1
      self.insert_tag_row(tag)
    logging.info("Total tag number: " + str(num))


  def load_git_data_to_db(self):
    self.import_branch_data()
    self.import_tag_data()
    self.import_commit_data()
