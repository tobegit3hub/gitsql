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
    connection = openmldb.dbapi.connect(repo_name, zk, zk_path)
    self.cursor = connection.cursor()


  def create_db_and_tables(cursor):
    logging.info("Try to create gitsql database")
    cursor.execute("CREATE DATABASE IF NOT EXISTS gitsql")

    logging.info("Try to create commit table")
    cursor.execute("CREATE TABLE commit (hexsha string, author string, email string, date int64, summary string,, size int, insertions int, deletions int, lines int, files int)")

    logging.info("Try to create branch table")
    cursor.execute("CREATE TABLE branch (name string, path string, commit string, remote bool, valid bool)")


  def insert_commit_row(cursor, commit):
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
      cursor.execute(sql)
    except Exception as e:
      logging.error("Fail to execute sql: {}, get error: {}".format(sql, e))


  def insert_branch_row(cursor, branch):
    sql = """INSERT INTO branch VALUES ("{}", "{}", "{}", {}, {})""".format(
      branch.name,
      branch.path,
      branch.commit.hexsha,
      branch.is_remote(),
      branch.is_valid()
    )

    try:
      cursor.execute(sql)
    except Exception as e:
      logging.error("Fail to execute sql: {}, get error: {}".format(sql, e))


  def import_commit_data(repo, cursor):
    commit_num = 0
    for commit in repo.iter_commits():
      commit_num += 1
      # Insert commit info to table
      insert_commit_row(cursor, commit)
    print("Total commit number: " + str(commit_num))


  def import_branch_data(repo, cursor):
    branch_num = 0
    for branch in repo.branches:
      branch_num += 1
      # Insert branch info to table
      insert_branch_row(cursor, branch)
    print("Total branch number: " + str(branch_num))
